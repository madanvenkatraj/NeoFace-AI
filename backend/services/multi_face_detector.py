import cv2
import numpy as np
import os
import uuid
import uuid
from typing import List, Dict, Any
from insightface.app import FaceAnalysis

# Assume a shared global model instance to save memory, or initialize on demand
class MultiFaceDetector:
    def __init__(self, model_name='buffalo_l', providers=['CUDAExecutionProvider', 'CPUExecutionProvider']):
        self.app = FaceAnalysis(name=model_name, providers=providers)
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
    def _crop_face(self, img: np.ndarray, bbox: np.ndarray, margin: float = 0.2) -> np.ndarray:
        h, w = img.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in bbox]
        
        # Add margin
        w_b = x2 - x1
        h_b = y2 - y1
        x1 = max(0, x1 - int(w_b * margin))
        y1 = max(0, y1 - int(h_b * margin))
        x2 = min(w, x2 + int(w_b * margin))
        y2 = min(h, y2 + int(h_b * margin))
        
        cropped = img[y1:y2, x1:x2]
        if cropped.size == 0:
            return np.zeros((256, 256, 3), dtype=np.uint8)
        return cv2.resize(cropped, (256, 256), interpolation=cv2.INTER_AREA)

    def _get_embedding(self, face) -> np.ndarray:
        return face.normed_embedding

    def detect_unique_faces(self, media_path: str, output_dir: str, is_video: bool = False, sim_threshold: float = 0.6) -> List[Dict[str, Any]]:
        unique_faces = []
        os.makedirs(output_dir, exist_ok=True)
        
        def process_frame(frame, frame_idx=0):
            faces = self.app.get(frame)
            for face in faces:
                emb = self._get_embedding(face)
                
                # Check against existing unique faces using cosine similarity
                is_unique = True
                for uf in unique_faces:
                    sim = np.dot(emb, uf['embedding'])
                    if sim > sim_threshold:
                        is_unique = False
                        break
                
                if is_unique:
                    face_id = str(uuid.uuid4())
                    cropped = self._crop_face(frame, face.bbox)
                    thumb_filename = f"thumb_{face_id}.jpg"
                    thumb_path = os.path.join(output_dir, thumb_filename)
                    cv2.imwrite(thumb_path, cropped)
                    
                    unique_faces.append({
                        'face_id': face_id,
                        'embedding': emb,
                        'thumbnail_url': f"/outputs/thumbnails/{thumb_filename}",
                        'bbox': face.bbox.tolist(),
                        'frame_idx': frame_idx
                    })

        if is_video:
            cap = cv2.VideoCapture(media_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if fps <= 0: fps = 30
            
            # Sample max 20 frames across the video to find unique faces (to avoid OOM and speed up)
            sample_interval = max(1, total_frames // 20)
            
            frame_idx = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_interval == 0:
                    process_frame(frame, frame_idx)
                
                frame_idx += 1
            cap.release()
        else:
            frame = cv2.imread(media_path)
            if frame is not None:
                process_frame(frame, 0)
                
        # Prepare for JSON response (remove numpy arrays)
        result = []
        for uf in unique_faces:
            res = uf.copy()
            res['embedding'] = uf['embedding'].tolist()
            result.append(res)
            
        return result

# Global instance
_detector_instance = None

def get_detector(use_cuda: bool = True):
    global _detector_instance
    current_use_cuda = getattr(_detector_instance, 'use_cuda', True) if _detector_instance else None
    
    if _detector_instance is None or current_use_cuda != use_cuda:
        _detector_instance = None
        import gc
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
            
        p = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_cuda else ['CPUExecutionProvider']
        _detector_instance = MultiFaceDetector(providers=p)
        _detector_instance.use_cuda = use_cuda
    return _detector_instance
