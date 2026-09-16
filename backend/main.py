from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid
from typing import List, Optional
from tasks import swap_video_task
from video_processor import process_detect_faces
from celery.result import AsyncResult

app = FastAPI(title="NeoFace AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/app/data/uploads"
OUTPUT_DIR = "/app/data/outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/api/history")
async def get_history():
    try:
        jobs = get_all_jobs()
        files = []
        
        for job in jobs:
            try:
                job['params'] = json.loads(job['params'])
            except:
                job['params'] = {}
                
            job_dict = {
                "task_id": job["task_id"],
                "filename": job["filename"],
                "state": job["state"],
                "created_at": job["created_at"],
                "frames_processed": job["frames_processed"] or 0,
                "params": job['params'],
                "url": "",
                "size": 0
            }
            
            if job["filename"] and job["state"] == "SUCCESS":
                job_dict["url"] = f"/outputs/{job['filename']}"
                file_path = os.path.join(OUTPUT_DIR, job["filename"])
                if os.path.exists(file_path):
                    job_dict["size"] = os.stat(file_path).st_size
                    
            files.append(job_dict)
            
        return {"history": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/idle")
async def get_system_idle():
    try:
        from db import get_idle_status
        return get_idle_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/metrics")
async def get_system_metrics():
    """Returns real-time GPU VRAM and Celery job load."""
    import torch
    
    gpu_metrics = {"available": False}
    if torch.cuda.is_available():
        try:
            free_mem, total_mem = torch.cuda.mem_get_info(0)
            used_mem = total_mem - free_mem
            gpu_metrics = {
                "available": True,
                "total_mb": total_mem // (1024 * 1024),
                "used_mb": used_mem // (1024 * 1024),
                "free_mb": free_mem // (1024 * 1024),
                "utilization_pct": round((used_mem / total_mem) * 100, 1)
            }
        except Exception:
            pass

    job_metrics = {"active": 0, "queued": 0}
    try:
        from celery_worker import celery_app
        i = celery_app.control.inspect()
        if i:
            active = i.active()
            reserved = i.reserved()
            if active:
                job_metrics["active"] = sum(len(tasks) for tasks in active.values())
            if reserved:
                job_metrics["queued"] = sum(len(tasks) for tasks in reserved.values())
    except Exception:
        pass

    return {
        "gpu": gpu_metrics,
        "jobs": job_metrics,
        "status": "warning" if (gpu_metrics.get("utilization_pct", 0) > 85 or job_metrics["active"] > 0) else "ok"
    }

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handles chunked or complete file uploads."""
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"file_id": file_id, "path": file_path, "filename": file.filename}

@app.post("/api/upload_url")
async def upload_url(url: str = Form(...)):
    """Downloads an image from a URL and saves it to the upload directory."""
    import requests
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        file_id = str(uuid.uuid4())
        ext = ".jpg" # Assume jpg for url images if we don't parse it
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
        
        with open(file_path, "wb") as buffer:
            for chunk in response.iter_content(chunk_size=8192):
                buffer.write(chunk)
                
        return {"file_id": file_id, "path": file_path, "filename": f"search_{file_id}{ext}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")

@app.post("/api/detect_faces")
async def detect_faces(file_path: str = Form(...)):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File not found")
        
    detection_data = process_detect_faces(file_path)
    if detection_data is None:
        raise HTTPException(status_code=500, detail="Failed to process image/video")
        
    return detection_data

from video_processor import process_detect_scenes

@app.post("/api/detect_scenes")
async def detect_scenes(file_path: str = Form(...)):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File not found")
    
    scenes = process_detect_scenes(file_path)
    return {"scenes": scenes}

@app.post("/api/swap")
async def start_swap(
    source_paths: List[str] = Form(...), 
    target_path: Optional[str] = Form(None),
    target_paths: List[str] = Form([]),
    trim_start: Optional[float] = Form(None),
    trim_end: Optional[float] = Form(None),
    strength: float = Form(1.0),
    enhance: bool = Form(True),
    face_mapping: Optional[str] = Form(None),
    mask_feather: float = Form(0.5),
    output_format: str = Form("mp4"),
    codec_quality: str = Form("medium"),
    skip_frames: int = Form(0),
    use_cuda: bool = Form(True)
):
    """Dispatch the swap job to Celery."""
    for sp in source_paths:
        if not os.path.exists(sp):
            raise HTTPException(status_code=400, detail=f"Source file not found: {sp}")
            
    targets = list(target_paths)
    if target_path:
        targets.append(target_path)
        
    if not targets:
        raise HTTPException(status_code=400, detail="No target files provided.")
        
    for tp in targets:
        if not os.path.exists(tp):
            raise HTTPException(status_code=400, detail=f"Target file not found: {tp}")
        
    task_ids = []
    for tp in targets:
        for sp in source_paths:
            # Validate extension
            ext = output_format.lower().strip('.')
            if ext not in ['mp4', 'avi', 'mkv']:
                ext = 'mp4'
                
            output_filename = f"out_{uuid.uuid4()}.{ext}"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            params = {
                "source_path": sp,
                "target_path": tp,
                "trim_start": trim_start,
                "trim_end": trim_end,
                "strength": strength,
                "enhance": enhance,
                "face_mapping": face_mapping,
                "mask_feather": mask_feather,
                "codec_quality": codec_quality,
                "output_format": output_format
            }
            task = swap_video_task.delay(sp, tp, output_path, trim_start, trim_end, strength, enhance, face_mapping, mask_feather, codec_quality, skip_frames, use_cuda)
            create_job(task.id, output_filename, params)
            task_ids.append(task.id)
    
    return {"task_ids": task_ids, "status": "QUEUED"}

@app.get("/api/jobs/{task_id}")
async def get_job_status(task_id: str):
    """Polling endpoint for job status."""
    task_result = AsyncResult(task_id)
    response = {
        "task_id": task_id,
        "state": task_result.state,
    }
    
    if task_result.state == 'PROGRESS':
        response['progress'] = task_result.info.get('progress', 0)
        response['status_msg'] = task_result.info.get('status', '')
    elif task_result.state == 'SUCCESS':
        response['result'] = task_result.result
    elif task_result.state == 'FAILURE':
        response['error'] = str(task_result.info)
        
    return JSONResponse(response)

@app.post("/api/target/detect")
async def detect_target_faces(file: UploadFile = File(...), use_cuda: bool = Form(True)):
    from services.multi_face_detector import get_detector
    detector_instance = get_detector(use_cuda=use_cuda)
    ext = file.filename.split('.')[-1]
    temp_path = os.path.join(UPLOAD_DIR, f"target_detect_{uuid.uuid4()}.{ext}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    is_video = ext.lower() in ['mp4', 'mov', 'avi', 'mkv', 'webm']
    out_dir = os.path.join(OUTPUT_DIR, 'thumbnails')
    faces = detector_instance.detect_unique_faces(temp_path, out_dir, is_video=is_video)
    
    return {"status": "SUCCESS", "target_path": temp_path, "faces": faces, "is_video": is_video}

@app.post("/api/source/automap")
async def automap_source_faces(
    file: UploadFile = File(...),
    target_embeddings: str = Form(...), # JSON string { target_face_id: [emb...] }
    use_cuda: bool = Form(True)
):
    import json
    from services.multi_face_detector import get_detector
    detector_instance = get_detector(use_cuda=use_cuda)
    import cv2
    import numpy as np

    ext = file.filename.split('.')[-1]
    temp_path = os.path.join(UPLOAD_DIR, f"automap_src_{uuid.uuid4()}.{ext}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    targets = json.loads(target_embeddings)
    
    img = cv2.imread(temp_path)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")
        
    src_faces = detector_instance.app.get(img)
    mappings = {}
    
    for t_id, t_emb_list in targets.items():
        t_emb = np.array(t_emb_list, dtype=np.float32)
        best_sim = -1.0
        best_face = None
        for s_face in src_faces:
            s_emb = s_face.normed_embedding
            sim = np.dot(t_emb, s_emb)
            if sim > best_sim:
                best_sim = float(sim)
                best_face = s_face
                
        if best_face is not None and best_sim > 0.4:
            face_id = str(uuid.uuid4())
            cropped = detector_instance._crop_face(img, best_face.bbox)
            thumb_filename = f"thumb_src_{face_id}.jpg"
            thumb_path = os.path.join(OUTPUT_DIR, 'thumbnails', thumb_filename)
            os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
            cv2.imwrite(thumb_path, cropped)
            
            mappings[t_id] = {
                "uploadedPath": thumb_path,
                "previewUrl": f"/outputs/thumbnails/{thumb_filename}"
            }
            
    return {"mappings": mappings}

@app.post("/api/target/swap")
async def multi_face_swap(
    target_path: str = Form(...),
    mapping_data: str = Form(...), # JSON string of mapping and embeddings
    is_video: bool = Form(...),
    use_cuda: bool = Form(True),
    quality_mode: str = Form("hd"),
    face_restoration: bool = Form(False),
    export_profile: str = Form("high")
):
    from tasks import multi_face_swap_task
    if not os.path.exists(target_path):
        raise HTTPException(status_code=400, detail="Target file not found.")
        
    ext = target_path.split('.')[-1]
    output_filename = f"out_multi_{uuid.uuid4()}.{ext}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    task = multi_face_swap_task.delay(target_path, output_path, mapping_data, is_video, use_cuda, quality_mode, face_restoration, export_profile)
    return {"task_id": task.id, "status": "QUEUED"}
