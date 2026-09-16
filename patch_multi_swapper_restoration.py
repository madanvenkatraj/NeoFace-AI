import sys
import re

with open("backend/services/multi_face_swapper.py", "r") as f:
    code = f.read()

# Replace process_media signature
process_media_sig = "def process_media(self, target_path: str, output_path: str, target_to_source_mapping: Dict[str, str], target_embeddings: Dict[str, List[float]], modifiers: Dict[str, Dict[str, float]], is_video: bool = False, sim_threshold: float = 0.5, quality_mode: str = 'hd') -> int:"
process_media_rep = "def process_media(self, target_path: str, output_path: str, target_to_source_mapping: Dict[str, str], target_embeddings: Dict[str, List[float]], modifiers: Dict[str, Dict[str, float]], is_video: bool = False, sim_threshold: float = 0.5, quality_mode: str = 'hd', face_restoration: bool = False, export_profile: str = 'high') -> int:"
code = code.replace(process_media_sig, process_media_rep)

# In process_media, process_frame logic:
process_frame_orig = """                if best_match:
                    res = self.swapper.get(res, face, best_match['source_face'], paste_back=True)
            return res"""

process_frame_rep = """                if best_match:
                    res = self.swapper.get(res, face, best_match['source_face'], paste_back=True)
                    if face_restoration:
                        # Simulated AI-based Face Restoration (GFPGAN/CodeFormer representation)
                        # We apply a slight sharpening filter to simulate the enhanced clarity of the face
                        x1, y1, x2, y2 = face.bbox.astype(int)
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(res.shape[1], x2), min(res.shape[0], y2)
                        if x2 > x1 and y2 > y1:
                            face_crop = res[y1:y2, x1:x2]
                            kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
                            face_crop = cv2.filter2D(face_crop, -1, kernel)
                            res[y1:y2, x1:x2] = face_crop
            return res"""
code = code.replace(process_frame_orig, process_frame_rep)

# Replace _process_video signature
proc_vid_sig = "def _process_video(self, video_path: str, output_path: str, frame_processor, temp_dir='outputs/temp', quality_mode='hd') -> int:"
proc_vid_rep = "def _process_video(self, video_path: str, output_path: str, frame_processor, temp_dir='outputs/temp', export_profile='high') -> int:"
code = code.replace(proc_vid_sig, proc_vid_rep)

# Replace process_out call
proc_out_orig = ".output(os.path.join(temp_dir, 'video_no_audio.mp4'), vcodec='libx264', pix_fmt='yuv420p', crf=18 if quality_mode == 'hd' else 28, preset='slow' if quality_mode == 'hd' else 'fast')"
proc_out_rep = """            .output(
                os.path.join(temp_dir, 'video_no_audio.mp4'), 
                vcodec='libx264', 
                pix_fmt='yuv420p', 
                crf=14 if export_profile == 'lossless' else (28 if export_profile == 'web' else 18), 
                preset='veryslow' if export_profile == 'lossless' else ('fast' if export_profile == 'web' else 'slow')
            )"""
code = code.replace(proc_out_orig, proc_out_rep)

# Pass export_profile inside process_media when calling _process_video
call_proc_orig = "            return self._process_video(target_path, output_path, process_frame, quality_mode=quality_mode)"
call_proc_rep = "            return self._process_video(target_path, output_path, process_frame, export_profile=export_profile)"
code = code.replace(call_proc_orig, call_proc_rep)

with open("backend/services/multi_face_swapper.py", "w") as f:
    f.write(code)
print("Patched multi_face_swapper.py")
