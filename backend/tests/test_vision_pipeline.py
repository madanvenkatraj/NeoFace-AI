import sys
import os
import cv2
import numpy as np
import unittest

# Append parent dir so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vision.face_detector import AdvancedFaceDetector, FaceDetection
from vision.video_tracker import VideoFaceTracker

class TestVisionPipeline(unittest.TestCase):
    def setUp(self):
        # We initialize the detector. Without insightface installed in this exact test env,
        # it falls back to mock mode gracefully (which is fine for unit testing math/logic)
        self.detector = AdvancedFaceDetector(model_name='buffalo_l', ctx_id=-1)
        self.tracker = VideoFaceTracker(similarity_threshold=0.5, max_missed_frames=3)
        
    def test_geometric_validation(self):
        # Valid proportions (roughly)
        valid_kps = np.array([
            [30, 40], # Left eye
            [70, 40], # Right eye
            [50, 60], # Nose tip
            [35, 80], # Left mouth
            [65, 80]  # Right mouth
        ])
        self.assertTrue(self.detector.validate_geometry(valid_kps), "Should validate normal facial geometry")
        
        # Invalid: Eyes further apart than mouth, but nose outside vertical boundaries
        invalid_nose_kps = np.array([
            [30, 40], 
            [70, 40], 
            [50, 20], # Nose above eyes (physiologically impossible)
            [35, 80], 
            [65, 80]  
        ])
        self.assertFalse(self.detector.validate_geometry(invalid_nose_kps), "Should reject nose out of vertical bounds")
        
        # Invalid: Eye distance too small compared to mouth distance (e.g. geometric pattern misidentified)
        invalid_ratio_kps = np.array([
            [48, 40], 
            [52, 40], # Distance = 4
            [50, 60], 
            [20, 80], 
            [80, 80]  # Distance = 60
        ])
        self.assertFalse(self.detector.validate_geometry(invalid_ratio_kps), "Should reject abnormal eye-to-mouth ratio")

    def test_pose_validation(self):
        # Normal pose [Pitch, Yaw, Roll]
        self.assertTrue(self.detector.validate_pose(np.array([10, -20, 5])))
        
        # Extreme profile (Yaw > 75)
        self.assertFalse(self.detector.validate_pose(np.array([10, 80, 5])))
        
        # Extreme Pitch (Pitch > 60)
        self.assertFalse(self.detector.validate_pose(np.array([-70, 10, 5])))

    def test_tracker_temporal_interpolation_and_identity(self):
        # Mock detection representing a face found by InsightFace
        det1 = FaceDetection(
            face_id="", bbox=[100.0, 100.0, 200.0, 200.0], 
            landmarks_5=np.array([[130, 140], [170, 140], [150, 160], [135, 180], [165, 180]]),
            landmarks_106=None, confidence=0.99, aligned_crop="",
            pose=np.zeros(3), embedding=np.ones(512) # Simulating ArcFace feature vector
        )
        
        # Frame 1: Register track
        res1 = self.tracker.update([det1])
        self.assertEqual(len(res1), 1)
        self.assertEqual(res1[0].face_id, "face_0001", "Tracker should assign a new persistent ID")
        
        # Frame 2: Occlusion (empty detections passed from detector)
        # Tracker should output interpolated frame via Kalman Filter
        res2 = self.tracker.update([])
        self.assertEqual(len(res2), 1, "Tracker should interpolate dropped frame due to motion blur")
        self.assertEqual(res2[0].face_id, "face_0001", "Interpolated track should maintain identity")
        # Confidence should decay
        self.assertTrue(res2[0].confidence < 0.99, "Confidence should decay during interpolation")
        
        # Frame 3-5: Missing for too many frames (max is 3 in our test setup logic)
        self.tracker.update([])
        self.tracker.update([])
        self.tracker.update([])
        res_empty = self.tracker.update([])
        self.assertEqual(len(res_empty), 0, "Should drop track after max_missed_frames exceeded")

if __name__ == '__main__':
    unittest.main()
