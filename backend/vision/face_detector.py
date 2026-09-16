import os
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
import onnxruntime as ort
from dataclasses import dataclass
import base64

# Conditional import for insightface to prevent crashes if not installed in env
try:
    from insightface.app import FaceAnalysis
    from insightface.utils import face_align
except ImportError:
    FaceAnalysis = None
    face_align = None

@dataclass
class FaceDetection:
    face_id: str
    bbox: List[float]
    landmarks_5: np.ndarray
    landmarks_106: Optional[np.ndarray]
    confidence: float
    aligned_crop: str
    pose: np.ndarray
    embedding: np.ndarray

class AdvancedFaceDetector:
    def __init__(self, model_name: str = 'buffalo_l', ctx_id: int = 0, det_thresh: float = 0.75):
        self.det_thresh = det_thresh
        
        if FaceAnalysis is None:
            print("Warning: InsightFace is not installed. Detector will run in dry/mock mode.")
            self.app = None
            return

        # Initialize InsightFace with buffalo_l (ResNet-50 backbone)
        # buffalo_l includes detection (retinaface) and recognition (arcface)
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        
        self.app = FaceAnalysis(
            name=model_name, 
            providers=providers, 
            allowed_modules=['detection', 'landmark_2d_106', 'recognition']
        )
        # Prepare the model with the specified context and confidence gate
        self.app.prepare(ctx_id=ctx_id, det_thresh=self.det_thresh)

    def validate_geometry(self, landmarks: np.ndarray) -> bool:
        """
        Validates 5-point facial landmarks to prevent false positives.
        Landmarks order: [left_eye, right_eye, nose, left_mouth, right_mouth]
        """
        if landmarks.shape != (5, 2):
            return False
        
        le, re, nose, lm, rm = landmarks
        
        # Check eye distance vs mouth distance
        eye_dist = np.linalg.norm(le - re)
        mouth_dist = np.linalg.norm(lm - rm)
        
        # Prevent division by zero
        if eye_dist == 0 or mouth_dist == 0:
            return False
            
        # Realistic anthropometric proportion: eye distance should be roughly comparable to mouth distance
        # Reject abnormal ratios which are usually background textures or non-human patterns
        ratio = eye_dist / mouth_dist
        if ratio < 0.4 or ratio > 2.5:
            return False
            
        eye_center = (le + re) / 2
        mouth_center = (lm + rm) / 2
        
        # Geometric Validation: Nose MUST be between eyes and mouth vertically
        if not (min(eye_center[1], mouth_center[1]) < nose[1] < max(eye_center[1], mouth_center[1])):
            return False
            
        return True

    def validate_pose(self, pose: np.ndarray) -> bool:
        """
        Validates 3D head pose (pitch, yaw, roll).
        Discard distorted detections that fall outside valid facial planes.
        """
        if pose is None or len(pose) != 3:
            return True # If pose is not available, bypass filter
            
        pitch, yaw, roll = pose
        
        # Reject extreme angles that suggest non-face or extreme profile
        # where rendering/swapping is functionally impossible.
        if abs(pitch) > 60 or abs(yaw) > 75 or abs(roll) > 70:
            return False
            
        return True

    def get_aligned_crop_base64(self, img: np.ndarray, landmarks: np.ndarray, crop_size: int = 512) -> str:
        """
        Returns normalized, affine-transformed aligned crops using Umeyama similarity transformation matrix.
        """
        if face_align is None:
            return ""

        # InsightFace's face_align uses standard ArcFace reference points
        aligned_img = face_align.norm_crop(img, landmark=landmarks, image_size=crop_size)
        
        # Convert the cropped image to a base64 string payload
        _, buffer = cv2.imencode('.jpg', aligned_img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        return base64.b64encode(buffer).decode('utf-8')

    def detect(self, image: np.ndarray) -> List[FaceDetection]:
        """
        Runs the detection pipeline on a single image.
        """
        if self.app is None:
            return []

        # app.get internally handles multi-scale pyramids through retinaface config
        faces = self.app.get(image)
        
        valid_faces = []
        for face in faces:
            # Confidence Gate (Redundant check as it's passed in prepare, but good for safety)
            if face.det_score < self.det_thresh:
                continue
                
            # Strict Anti-False-Positive Filtering
            if not self.validate_geometry(face.kps):
                continue
                
            # Pose constraint checking
            if hasattr(face, 'pose') and not self.validate_pose(face.pose):
                continue
                
            # Alignment and Crop Normalization (512x512)
            aligned_crop_b64 = self.get_aligned_crop_base64(image, face.kps)
            
            # Extract 106 dense landmarks if model supports it
            landmarks_106 = face.landmark_2d_106 if hasattr(face, 'landmark_2d_106') else None
            
            det = FaceDetection(
                face_id="", # Face ID will be assigned downstream by the VideoTracker
                bbox=face.bbox.tolist(),
                landmarks_5=face.kps,
                landmarks_106=landmarks_106,
                confidence=float(face.det_score),
                aligned_crop=aligned_crop_b64,
                pose=face.pose if hasattr(face, 'pose') else np.zeros(3),
                embedding=face.embedding if hasattr(face, 'embedding') else np.zeros(512)
            )
            valid_faces.append(det)
            
        return valid_faces
