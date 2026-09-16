from celery_worker import celery_app
from video_processor import process_video_swap
import os
import json
from db import update_job_state

@celery_app.task(bind=True)
def swap_video_task(self, source_path: str, target_path: str, output_path: str, trim_start: float = None, trim_end: float = None, strength: float = 1.0, enhance: bool = True, face_mapping: str = None, mask_feather: float = 0.5, codec_quality: str = 'medium', skip_frames: int = 0, use_cuda: bool = True):
    """
    Celery task to run the video face swapping pipeline.
    """
    import time
    frames_processed_ref = [0]
    def progress_callback(progress: int, status: str, frame_idx: int = 0):
        frames_processed_ref[0] = max(frames_processed_ref[0], frame_idx)
        self.update_state(state='PROGRESS', meta={'progress': progress, 'status': status})
        try:
            update_job_state(self.request.id, 'PROGRESS', progress, frame_idx)
        except Exception:
            pass
    
    try:
        start_time = time.time()
        frames_processed = process_video_swap(source_path, target_path, output_path, progress_callback, trim_start, trim_end, strength, enhance, face_mapping, mask_feather, codec_quality, skip_frames, use_cuda=use_cuda)
        update_job_state(self.request.id, 'SUCCESS', 100, frames_processed)
        end_time = time.time()
        process_time = end_time - start_time
        fps = frames_processed / process_time if process_time > 0 and frames_processed else 0

        return {
            "status": "COMPLETED", 
            "output_path": output_path,
            "metrics": {
                "process_time_s": process_time,
                "frames": frames_processed or 1,
                "fps": fps
            }
        }
    except Exception as e:
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        try:
            update_job_state(self.request.id, 'FAILURE', frames_processed=frames_processed_ref[0])
        except Exception:
            pass
        raise e

@celery_app.task(bind=True)
def multi_face_swap_task(self, target_path: str, output_path: str, mapping_data: str, is_video: bool, use_cuda: bool = True, quality_mode: str = 'hd', face_restoration: bool = False, export_profile: str = 'high'):
    import time
    from services.multi_face_swapper import get_multi_swapper
    swapper_instance = get_multi_swapper(use_cuda=use_cuda)
    try:
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Initializing multi-swap...'})
        data = json.loads(mapping_data)
        target_to_source = data.get('mapping', {})
        target_embeddings = data.get('embeddings', {})
        modifiers = data.get('modifiers', {})
        landmark_modifiers = data.get('landmark_modifiers', {})
        source_bboxes = data.get('source_bboxes', {})
        
        start_time = time.time()
        
        frames_processed = swapper_instance.process_media(
            target_path, 
            output_path, 
            target_to_source, 
            target_embeddings, 
            modifiers,
            landmark_modifiers,
            source_bboxes,
            is_video=is_video,
            quality_mode=quality_mode,
            face_restoration=face_restoration,
            export_profile=export_profile
        )
        
        end_time = time.time()
        process_time = end_time - start_time
        fps = frames_processed / process_time if process_time > 0 else 0
        
        return {
            "status": "COMPLETED", 
            "output_path": output_path,
            "metrics": {
                "process_time_s": process_time,
                "frames": frames_processed,
                "fps": fps
            }
        }
    except Exception as e:
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        try:
            update_job_state(self.request.id, 'FAILURE')
        except Exception:
            pass
        raise e

