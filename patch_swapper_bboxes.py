import sys

with open("backend/services/multi_face_swapper.py", "r") as f:
    code = f.read()

sig_orig = "def process_media(self, target_path: str, output_path: str, target_to_source_mapping: dict, target_embeddings: dict, modifiers: dict, landmark_modifiers: dict, is_video: bool = False, sim_threshold: float = 0.5, quality_mode: str = 'hd', face_restoration: bool = False, export_profile: str = 'high') -> int:"
sig_new = "def process_media(self, target_path: str, output_path: str, target_to_source_mapping: dict, target_embeddings: dict, modifiers: dict, landmark_modifiers: dict, source_bboxes: dict, is_video: bool = False, sim_threshold: float = 0.5, quality_mode: str = 'hd', face_restoration: bool = False, export_profile: str = 'high') -> int:"
code = code.replace(sig_orig, sig_new)

loop_orig = """            if s_faces:
                s_face = max(s_faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
                t_emb = np.array(target_embeddings[t_id], dtype=np.float32)"""
loop_new = """            if s_faces:
                s_bbox = source_bboxes.get(t_id)
                if s_bbox:
                    def box_center(b): return ((b[0]+b[2])/2, (b[1]+b[3])/2)
                    scx, scy = box_center(s_bbox)
                    s_face = min(s_faces, key=lambda f: (box_center(f.bbox)[0]-scx)**2 + (box_center(f.bbox)[1]-scy)**2)
                else:
                    s_face = max(s_faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
                t_emb = np.array(target_embeddings[t_id], dtype=np.float32)"""
code = code.replace(loop_orig, loop_new)

with open("backend/services/multi_face_swapper.py", "w") as f:
    f.write(code)

print("Patched swapper to use source_bboxes")
