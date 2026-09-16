import sys

with open("backend/tasks.py", "r") as f:
    code = f.read()

get_mods = "        modifiers = data.get('modifiers', {})"
get_mods_rep = "        modifiers = data.get('modifiers', {})\n        landmark_modifiers = data.get('landmark_modifiers', {})"
code = code.replace(get_mods, get_mods_rep)

call_proc = "            modifiers,\n            is_video=is_video,"
call_proc_rep = "            modifiers,\n            landmark_modifiers,\n            is_video=is_video,"
code = code.replace(call_proc, call_proc_rep)

with open("backend/tasks.py", "w") as f:
    f.write(code)

with open("backend/services/multi_face_swapper.py", "r") as f:
    m_code = f.read()

sig_orig = "def process_media(self, target_path: str, output_path: str, target_to_source_mapping: Dict[str, str], target_embeddings: Dict[str, List[float]], modifiers: Dict[str, Dict[str, float]], is_video: bool = False, sim_threshold: float = 0.5, quality_mode: str = 'hd', face_restoration: bool = False, export_profile: str = 'high') -> int:"
sig_rep = "def process_media(self, target_path: str, output_path: str, target_to_source_mapping: Dict[str, str], target_embeddings: Dict[str, List[float]], modifiers: Dict[str, Dict[str, float]], landmark_modifiers: Dict[str, Dict[str, float]], is_video: bool = False, sim_threshold: float = 0.5, quality_mode: str = 'hd', face_restoration: bool = False, export_profile: str = 'high') -> int:"
m_code = m_code.replace(sig_orig, sig_rep)


proc_frame_orig = """            for face in faces:
                best_match = None
                best_sim = -1
                for t_id, mapping in active_mapping.items():
                    sim = np.dot(face.normed_embedding, mapping['target_embedding'])
                    if sim > best_sim:
                        best_sim = sim
                        best_match = mapping
                
                # Using 0.45 as threshold for ArcFace cosine similarity
                if best_match and best_sim > sim_threshold:
                    res = self.swapper.get(res, face, best_match['source_face'], paste_back=True)"""

proc_frame_rep = """            for face in faces:
                best_match = None
                best_sim = -1
                best_tid = None
                for t_id, mapping in active_mapping.items():
                    sim = np.dot(face.normed_embedding, mapping['target_embedding'])
                    if sim > best_sim:
                        best_sim = sim
                        best_match = mapping
                        best_tid = t_id
                
                # Using 0.45 as threshold for ArcFace cosine similarity
                if best_match and best_sim > sim_threshold:
                    if best_tid in landmark_modifiers:
                        lmods = landmark_modifiers[best_tid]
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

                    res = self.swapper.get(res, face, best_match['source_face'], paste_back=True)"""
m_code = m_code.replace(proc_frame_orig, proc_frame_rep)

with open("backend/services/multi_face_swapper.py", "w") as f:
    f.write(m_code)

print("Patched backend for landmark modifiers")
