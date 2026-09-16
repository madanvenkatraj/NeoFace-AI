import numpy as np
from typing import List, Dict, Optional, Tuple
from .face_detector import FaceDetection

class KalmanFilter2D:
    """
    2D Kalman Filter for smoothing bounding box trajectories 
    during motion blur or temporary occlusion.
    """
    def __init__(self, init_pos: Tuple[float, float]):
        # State: [x, y, dx, dy]
        self.state = np.array([[init_pos[0]], [init_pos[1]], [0.0], [0.0]], dtype=np.float32)
        # Covariance matrix
        self.P = np.eye(4, dtype=np.float32) * 10.0
        # State transition matrix
        self.F = np.array([[1, 0, 1, 0], 
                           [0, 1, 0, 1], 
                           [0, 0, 1, 0], 
                           [0, 0, 0, 1]], dtype=np.float32)
        # Measurement matrix
        self.H = np.array([[1, 0, 0, 0], 
                           [0, 1, 0, 0]], dtype=np.float32)
        # Measurement noise covariance
        self.R = np.eye(2, dtype=np.float32) * 5.0
        # Process noise covariance
        self.Q = np.eye(4, dtype=np.float32) * 0.1
        
    def predict(self) -> np.ndarray:
        # Predict next state
        self.state = np.dot(self.F, self.state)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        return self.state[:2].flatten()
        
    def update(self, measurement: Tuple[float, float]):
        z = np.array([[measurement[0]], [measurement[1]]])
        y = z - np.dot(self.H, self.state)
        S = np.dot(np.dot(self.H, self.P), self.H.T) + self.R
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        
        self.state = self.state + np.dot(K, y)
        self.P = self.P - np.dot(np.dot(K, self.H), self.P)

class TrackedFace:
    """
    Represents a persistent facial identity tracked across video frames.
    """
    def __init__(self, face_id: str, initial_det: FaceDetection):
        self.face_id = face_id
        self.last_det = initial_det
        self.embedding = initial_det.embedding
        self.missed_frames = 0
        
        # Initialize Kalman filters for the bounding box corners (Top-Left and Bottom-Right)
        bbox = initial_det.bbox
        self.kf_tl = KalmanFilter2D((bbox[0], bbox[1]))
        self.kf_br = KalmanFilter2D((bbox[2], bbox[3]))
        
        # EMA (Exponential Moving Average) for landmark smoothing
        self.ema_landmarks = initial_det.landmarks_5.copy()
        self.ema_alpha = 0.7  # High responsiveness (1.0 = no smoothing)

    def predict(self) -> Tuple[np.ndarray, np.ndarray]:
        pred_tl = self.kf_tl.predict()
        pred_br = self.kf_br.predict()
        return pred_tl, pred_br

    def update(self, det: FaceDetection):
        self.last_det = det
        self.missed_frames = 0
        
        # Identity Persistence: Adapt the embedding slightly over time to handle lighting/angle changes
        self.embedding = 0.9 * self.embedding + 0.1 * det.embedding
        self.embedding = self.embedding / np.linalg.norm(self.embedding)
        
        # Update Kalman Filters with current bbox
        bbox = det.bbox
        self.kf_tl.update((bbox[0], bbox[1]))
        self.kf_br.update((bbox[2], bbox[3]))
        
        # Landmark Smoothing: Apply EMA to reduce jitter
        self.ema_landmarks = self.ema_alpha * det.landmarks_5 + (1 - self.ema_alpha) * self.ema_landmarks
        
class VideoFaceTracker:
    def __init__(self, similarity_threshold: float = 0.5, max_missed_frames: int = 5):
        self.tracks: Dict[str, TrackedFace] = {}
        self.next_id = 1
        self.similarity_threshold = similarity_threshold
        self.max_missed_frames = max_missed_frames
        
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity between two ArcFace embeddings."""
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8))

    def update(self, detections: List[FaceDetection]) -> List[FaceDetection]:
        """
        Takes raw frame detections, maps them to persistent tracks, 
        and applies smoothing & interpolation.
        """
        # Predict next positions for all current tracks
        for track in self.tracks.values():
            track.predict()
            
        unmatched_dets = detections.copy()
        matched_tracks = set()
        
        processed_detections = []
        
        # Step 1: Match by Embedding Similarity (ArcFace via Cosine Distance)
        for track_id, track in self.tracks.items():
            best_match_idx = -1
            best_sim = -1
            
            for i, det in enumerate(unmatched_dets):
                sim = self._cosine_similarity(track.embedding, det.embedding)
                if sim > best_sim and sim > self.similarity_threshold:
                    best_sim = sim
                    best_match_idx = i
                    
            if best_match_idx != -1:
                # We found a matching identity in this frame
                matched_det = unmatched_dets.pop(best_match_idx)
                track.update(matched_det)
                matched_tracks.add(track_id)
                
                # Update the detection with smoothed values for the pipeline
                matched_det.face_id = track.face_id
                matched_det.landmarks_5 = track.ema_landmarks
                
                # Optionally smooth the bbox via kalman state instead of raw detection
                # state_tl = track.kf_tl.state[:2].flatten()
                # state_br = track.kf_br.state[:2].flatten()
                # matched_det.bbox = [state_tl[0], state_tl[1], state_br[0], state_br[1]]
                
                processed_detections.append(matched_det)
                
        # Step 2: Handle unmatched detections (New faces entering the scene)
        for det in unmatched_dets:
            new_id = f"face_{self.next_id:04d}"
            self.next_id += 1
            self.tracks[new_id] = TrackedFace(new_id, det)
            det.face_id = new_id
            processed_detections.append(det)
            
        # Step 3: Handle unmatched tracks (Occlusion & Motion Blur Recovery)
        tracks_to_remove = []
        for track_id, track in self.tracks.items():
            if track_id not in matched_tracks:
                track.missed_frames += 1
                
                # If face is lost for 1-3 frames, interpolate position based on momentum
                if track.missed_frames <= 3:
                    pred_tl, pred_br = track.predict()
                    interpolated_bbox = [float(pred_tl[0]), float(pred_tl[1]), float(pred_br[0]), float(pred_br[1])]
                    
                    # Create an interpolated "ghost" detection to maintain continuity
                    mock_det = FaceDetection(
                        face_id=track.face_id,
                        bbox=interpolated_bbox,
                        landmarks_5=track.ema_landmarks,
                        landmarks_106=track.last_det.landmarks_106,
                        confidence=track.last_det.confidence * 0.9, # Decay confidence over time
                        aligned_crop=track.last_det.aligned_crop,
                        pose=track.last_det.pose,
                        embedding=track.embedding
                    )
                    processed_detections.append(mock_det)
                    
                # Drop track entirely if lost for too long
                if track.missed_frames > self.max_missed_frames:
                    tracks_to_remove.append(track_id)
                    
        # Garbage Collection
        for track_id in tracks_to_remove:
            del self.tracks[track_id]
            
        return processed_detections
