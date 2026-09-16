import os
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import onnxruntime
import ffmpeg
import shutil
import gc
import subprocess
import re
from typing import Callable, Optional

# Disable MPS/CoreML if onmac, but we are optimizing for CUDA
providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']

class FaceSwapper:
    def __init__(self, model_dir: str = "../models", providers: list = ['CUDAExecutionProvider', 'CPUExecutionProvider']):
        self.app = FaceAnalysis(name='buffalo_l', root=model_dir, providers=providers)
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
        swapper_path = os.path.join(model_dir, 'inswapper_128.onnx')
        self.swapper = insightface.model_zoo.get_model(swapper_path, download=False, download_zip=False)
        
        # Load GFPGAN for face enhancement
        try:
            from gfpgan import GFPGANer
            gfpgan_path = os.path.join(model_dir, 'GFPGANv1.4.pth')
            self.enhancer = GFPGANer(model_path=gfpgan_path, upscale=1, arch='clean', channel_multiplier=2, bg_upsampler=None)
        except ImportError:
            self.enhancer = None
            print("GFPGAN not found, continuing without enhancement")

    def get_face(self, img: np.ndarray):
        faces = self.app.get(img)
        if len(faces) == 0:
            return None
        # Return the largest face by bounding box area
        return max(faces, key=lambda face: (face.bbox[2]-face.bbox[0]) * (face.bbox[3]-face.bbox[1]))

    def swap_face(self, source_img: np.ndarray, target_img: np.ndarray, enhance: bool = True, strength: float = 1.0, mask_feather: float = 0.5):
        source_face = self.get_face(source_img)
        if source_face is None:
            return target_img

        target_faces = self.app.get(target_img)
        if len(target_faces) == 0:
            return target_img

        res = target_img.copy()
        for target_face in target_faces:
            res = self.swapper.get(res, target_face, source_face, paste_back=True)
            
            if mask_feather > 0:
                # Apply simulated mask feathering by blending the bounding box edges
                box = target_face.bbox.astype(int)
                x1, y1, x2, y2 = max(0, box[0]), max(0, box[1]), min(res.shape[1], box[2]), min(res.shape[0], box[3])
                mask = np.zeros_like(res, dtype=np.float32)
                mask[y1:y2, x1:x2] = 1.0
                k_size = int(max(x2-x1, y2-y1) * mask_feather)
                if k_size % 2 == 0: k_size += 1
                mask = cv2.GaussianBlur(mask, (k_size, k_size), 0)
                res = (res * mask + target_img * (1.0 - mask)).astype(np.uint8)
                
        if enhance and self.enhancer is not None:
            _, _, res = self.enhancer.enhance(res, has_aligned=False, only_center_face=False, paste_back=True)
        
        if strength < 1.0:
            res = cv2.addWeighted(res, strength, target_img, 1.0 - strength, 0)
            
        return res

    def swap_faces_tracked(self, trackers: list, target_img: np.ndarray, enhance: bool = True, strength: float = 1.0, mask_feather: float = 0.5):
        faces = self.app.get(target_img)
        if not faces:
            return target_img
            
        res = target_img.copy()
        for face in faces:
            best_match = None
            best_sim = -1
            for tracker in trackers:
                sim = np.dot(face.normed_embedding, tracker['target_emb'])
                if sim > best_sim:
                    best_sim = sim
                    best_match = tracker
            
            # Using 0.45 as threshold for ArcFace cosine similarity
            if best_match and best_sim > 0.45:
                res = self.swapper.get(res, face, best_match['source_face'], paste_back=True)
                
                if mask_feather > 0:
                    box = face.bbox.astype(int)
                    x1, y1, x2, y2 = max(0, box[0]), max(0, box[1]), min(res.shape[1], box[2]), min(res.shape[0], box[3])
                    mask = np.zeros_like(res, dtype=np.float32)
                    mask[y1:y2, x1:x2] = 1.0
                    k_size = int(max(x2-x1, y2-y1) * mask_feather)
                    if k_size % 2 == 0: k_size += 1
                    mask = cv2.GaussianBlur(mask, (k_size, k_size), 0)
                    res = (res * mask + target_img * (1.0 - mask)).astype(np.uint8)
                
        if enhance and self.enhancer is not None:
            _, _, res = self.enhancer.enhance(res, has_aligned=False, only_center_face=False, paste_back=True)
            
        if strength < 1.0:
            res = cv2.addWeighted(res, strength, target_img, 1.0 - strength, 0)
            
        return res

_swapper_instance = None

def get_swapper(use_cuda: bool = True):
    global _swapper_instance
    
    current_use_cuda = getattr(_swapper_instance, 'use_cuda', True) if _swapper_instance else None
    
    if _swapper_instance is None or current_use_cuda != use_cuda:
        _swapper_instance = None
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
            
        p = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_cuda else ['CPUExecutionProvider']
        _swapper_instance = FaceSwapper(model_dir="/app/models", providers=p)
        _swapper_instance.use_cuda = use_cuda
    return _swapper_instance

def get_first_frame(file_path: str):
    if file_path.lower().endswith(('.mp4', '.mov', '.avi')):
        cap = cv2.VideoCapture(file_path)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return None
        return frame
    else:
        return cv2.imread(file_path)

def process_detect_faces(file_path: str, use_cuda: bool = True):
    swapper = get_swapper(use_cuda=use_cuda)
    img = get_first_frame(file_path)
        
    if img is None:
        return None
        
    faces = swapper.app.get(img)
    h, w = img.shape[:2]
    
    boxes = []
    for i, face in enumerate(faces):
        bbox = face.bbox.tolist()
        boxes.append({
            "id": i,
            "box": bbox,
            "score": float(face.det_score)
        })
        
    return {"width": w, "height": h, "faces": boxes}

def process_detect_scenes(video_path: str, threshold: float = 0.3, use_cuda: bool = True):
    """Uses FFmpeg's scene filter to detect timestamps of major visual cuts."""
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-filter:v', f"select='gt(scene,{threshold})',showinfo",
        '-f', 'null',
        '-'
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    matches = re.findall(r'pts_time:([0-9\.]+)', result.stderr)
    cuts = [0.0] + [float(m) for m in matches]
    
    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe['streams'][0]['duration'])
        if cuts[-1] < duration:
            cuts.append(duration)
    except Exception:
        pass
        
    scenes = []
    for i in range(len(cuts)-1):
        start = round(cuts[i], 1)
        end = round(cuts[i+1], 1)
        if end - start > 0.5:
            scenes.append({"start": start, "end": end})
            
    return scenes

def process_video_swap(
    source_path: str, 
    target_path: str, 
    output_path: str, 
    progress_callback: Optional[Callable[[int, str, int], None]] = None,
    trim_start: Optional[float] = None,
    trim_end: Optional[float] = None,
    strength: float = 1.0,
    enhance: bool = True,
    face_mapping: Optional[str] = None,
    mask_feather: float = 0.5,
    codec_quality: str = 'medium',
    skip_frames: int = 0,
    use_cuda: bool = True
):
    """
    Extract frames -> Detect & Swap -> Enhance -> Remux Audio
    """
    if progress_callback:
        progress_callback(0, "Initializing models", 0)
        
    swapper = get_swapper(use_cuda=use_cuda)
    source_img = cv2.imread(source_path)
    if source_img is None:
        raise ValueError("Could not read source image")

    # Build trackers if face mapping is provided
    trackers = None
    if face_mapping and face_mapping != "{}" and face_mapping != "null":
        import json
        mapping = json.loads(face_mapping)
        if mapping:
            target_reference_img = get_first_frame(target_path)
            if target_reference_img is not None:
                source_faces = swapper.app.get(source_img)
                target_faces = swapper.app.get(target_reference_img)
                
                trackers = []
                for t_idx_str, s_idx in mapping.items():
                    t_idx = int(t_idx_str)
                    s_idx = int(s_idx)
                    if t_idx < len(target_faces) and s_idx < len(source_faces):
                        trackers.append({
                            'target_emb': target_faces[t_idx].normed_embedding,
                            'source_face': source_faces[s_idx]
                        })

    temp_dir = os.path.join(os.path.dirname(output_path), f"temp_{os.path.basename(output_path)}")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Get video info first to calculate framerate
    probe = ffmpeg.probe(target_path)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    
    fps_val = 30.0
    try:
        fps_val = eval(video_info.get('r_frame_rate', '30/1'))
    except:
        pass

    # Extract audio
    if progress_callback:
        progress_callback(5, "Extracting audio", 0)
    audio_path = os.path.join(temp_dir, "audio.aac")
    
    in_kwargs = {}
    if trim_start is not None:
        in_kwargs['ss'] = trim_start
    if trim_end is not None and trim_start is not None:
        in_kwargs['t'] = trim_end - trim_start
    elif trim_end is not None:
        in_kwargs['to'] = trim_end

    audio_kwargs = dict(in_kwargs)
    
    adjusted_trim_start = trim_start or 0.0
    if skip_frames > 0:
        adjusted_trim_start += (skip_frames / fps_val)
        
    if adjusted_trim_start > 0:
        audio_kwargs['ss'] = adjusted_trim_start
    if trim_end is not None and adjusted_trim_start > 0:
        if trim_start is not None:
             audio_kwargs.pop('t', None)
        audio_kwargs['to'] = trim_end
        
    try:
        ffmpeg.input(target_path, **audio_kwargs).output(audio_path, vn=None, acodec='copy').overwrite_output().run(quiet=True)
        has_audio = True
    except ffmpeg.Error:
        has_audio = False
    
    # Calculate total frames (approximation)
    try:
        total_frames = int(video_info.get('nb_frames', 0))
        if trim_start is not None or trim_end is not None:
            # Estimate new total frames based on duration
            fps = eval(video_info.get('r_frame_rate', '30/1'))
            duration = (trim_end if trim_end else float(video_info.get('duration', 0))) - (trim_start if trim_start else 0)
            total_frames = int(duration * fps)
    except (ValueError, TypeError, ZeroDivisionError):
        total_frames = 0
        
    if progress_callback:
        progress_callback(10, "Extracting frames", 0)

    # Read frames using FFmpeg to avoid OpenCV memory leaks on large videos
    process_in = (
        ffmpeg
        .input(target_path, **in_kwargs)
        .output('pipe:', format='rawvideo', pix_fmt='bgr24')
        .run_async(pipe_stdout=True, quiet=True)
    )

    # Quality mapping
    crf_map = {'high': 18, 'medium': 23, 'low': 28}
    preset_map = {'high': 'slow', 'medium': 'medium', 'low': 'fast'}
    crf = crf_map.get(codec_quality, 23)
    preset = preset_map.get(codec_quality, 'medium')

    process_out = (
        ffmpeg
        .input('pipe:', format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(width, height))
        .output(os.path.join(temp_dir, 'video_no_audio.mp4'), vcodec='libx264', pix_fmt='yuv420p', crf=crf, preset=preset)
        .overwrite_output()
        .run_async(pipe_stdin=True, quiet=True)
    )

    frame_idx = 0
    in_bytes = width * height * 3

    while True:
        in_frame = process_in.stdout.read(in_bytes)
        if not in_frame:
            break

        if frame_idx < skip_frames:
            frame_idx += 1
            if progress_callback and frame_idx % 30 == 0:
                pct = min(10, int((frame_idx / skip_frames) * 10)) if skip_frames > 0 else 10
                progress_callback(pct, f"Skipping to frame {frame_idx}/{skip_frames}...", frame_idx)
            continue

        frame = np.frombuffer(in_frame, np.uint8).reshape([height, width, 3])
        
        # Swap
        if trackers:
            swapped_frame = swapper.swap_faces_tracked(trackers, frame, enhance=enhance, strength=strength, mask_feather=mask_feather)
        else:
            swapped_frame = swapper.swap_face(source_img, frame, enhance=enhance, strength=strength, mask_feather=mask_feather)
            
        process_out.stdin.write(swapped_frame.tobytes())
        
        frame_idx += 1
        if progress_callback and frame_idx % 30 == 0:
            pct = 10 + min(80, int((frame_idx / total_frames) * 80)) if total_frames > 0 else 10
            progress_callback(pct, f"Swapped frame {frame_idx}/{total_frames if total_frames > 0 else 'Unknown'}", frame_idx)
            
        # Memory cleanup
        if frame_idx % 100 == 0:
            gc.collect()

    process_out.stdin.close()
    process_out.wait()
    process_in.wait()

    if progress_callback:
        progress_callback(95, "Remuxing audio", frame_idx)

    # Remux
    video_no_audio = ffmpeg.input(os.path.join(temp_dir, 'video_no_audio.mp4'))
    if has_audio:
        audio = ffmpeg.input(audio_path)
        out = ffmpeg.output(video_no_audio, audio, output_path, vcodec='copy', acodec='aac').overwrite_output()
    else:
        out = ffmpeg.output(video_no_audio, output_path, vcodec='copy').overwrite_output()
        
    out.run(quiet=True)
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    if progress_callback:
        progress_callback(100, "Completed", frame_idx)

    return frame_idx


