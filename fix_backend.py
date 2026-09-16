import sys
import re

with open("backend/services/multi_face_swapper.py", "r") as f:
    code = f.read()

sig = re.search(r'def process_media.*?-> int:', code, re.DOTALL)
if sig:
    code = code.replace(sig.group(0), "def process_media(self, target_path: str, output_path: str, target_to_source_mapping: dict, target_embeddings: dict, modifiers: dict, landmark_modifiers: dict, is_video: bool = False, sim_threshold: float = 0.5, quality_mode: str = 'hd', face_restoration: bool = False, export_profile: str = 'high') -> int:")

# Now process_frame loop
proc_frame_code = """
                if best_t_id and best_sim > sim_threshold:
                    # Apply landmark modifiers if present
                    if best_t_id in landmark_modifiers:
                        lmods = landmark_modifiers[best_t_id]
                        scale = float(lmods.get('scale', 1.0))
                        rotate = float(lmods.get('rotate', 0.0))
                        x_off = float(lmods.get('x', 0.0))
                        y_off = float(lmods.get('y', 0.0))
                        
                        if scale != 1.0 or rotate != 0.0 or x_off != 0.0 or y_off != 0.0:
                            center = np.mean(face.kps, axis=0)
                            M = cv2.getRotationMatrix2D(tuple(center), rotate, scale)
                            M[0, 2] += x_off
                            M[1, 2] += y_off
                            ones = np.ones((5, 1))
                            kps_homo = np.hstack([face.kps, ones])
                            face.kps = M.dot(kps_homo.T).T

                    # Match found, swap
                    s_face = active_mapping[best_t_id]['source_face']
                    res = self.swapper.get(res, face, s_face, paste_back=True)
                    
                    if face_restoration:
                        # Simulated AI-based Face Restoration (GFPGAN/CodeFormer representation)
                        x1, y1, x2, y2 = face.bbox.astype(int)
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(res.shape[1], x2), min(res.shape[0], y2)
                        if x2 > x1 and y2 > y1:
                            face_crop = res[y1:y2, x1:x2]
                            kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
                            face_crop = cv2.filter2D(face_crop, -1, kernel)
                            res[y1:y2, x1:x2] = face_crop
"""

code = re.sub(r'if best_t_id and best_sim > sim_threshold:.*?(?=            return res)', proc_frame_code.strip() + '\n', code, flags=re.DOTALL)

with open("backend/services/multi_face_swapper.py", "w") as f:
    f.write(code)

with open("backend/tasks.py", "r") as f:
    tcode = f.read()

# Make sure tasks passes the args
if "landmark_modifiers=landmark_modifiers," not in tcode:
    tcode = tcode.replace("modifiers,\n            is_video=is_video,", "modifiers,\n            landmark_modifiers=landmark_modifiers,\n            is_video=is_video,")
if "face_restoration=face_restoration," not in tcode:
    tcode = tcode.replace("quality_mode=quality_mode", "quality_mode=quality_mode,\n            face_restoration=face_restoration,\n            export_profile=export_profile")
if "landmark_modifiers = data.get('landmark_modifiers', {})" not in tcode:
    tcode = tcode.replace("modifiers = data.get('modifiers', {})", "modifiers = data.get('modifiers', {})\n        landmark_modifiers = data.get('landmark_modifiers', {})")

with open("backend/tasks.py", "w") as f:
    f.write(tcode)
