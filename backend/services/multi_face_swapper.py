import cv2
import numpy as np
import os
import shutil
import subprocess
import ffmpeg
import insightface
from typing import Dict, List, Any

class MultiFaceSwapper:
    def __init__(self, model_name='buffalo_l', swapper_model_path='inswapper_128.onnx', providers=['CUDAExecutionProvider', 'CPUExecutionProvider']):
        self.app = insightface.app.FaceAnalysis(name=model_name, providers=providers)
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        self.swapper = insightface.model_zoo.get_model(swapper_model_path, providers=providers)
        
    def _get_embedding(self, face) -> np.ndarray:
        return face.normed_embedding

    def process_media(self, target_path: str, output_path: str, target_to_source_mapping: dict, target_embeddings: dict, modifiers: dict, landmark_modifiers: dict, source_bboxes: dict, is_video: bool = False, sim_threshold: float = 0.5, quality_mode: str = 'hd', face_restoration: bool = False, export_profile: str = 'high') -> int:
        # 1. Extract source faces for mapping
        # mapping format: target_face_id (str) -> source_image_path (str)
        # target_embeddings format: target_face_id (str) -> embedding (list of floats)
        # modifiers format: target_face_id (str) -> { "expansion": float, "erosion": float }
        
        active_mapping = {}
        for t_id, s_path in target_to_source_mapping.items():
            if not s_path: continue
            s_img = cv2.imread(s_path)
            if s_img is None: continue
            s_faces = self.app.get(s_img)
            if s_faces:
                s_bbox = source_bboxes.get(t_id)
                if s_bbox:
                    def box_center(b): return ((b[0]+b[2])/2, (b[1]+b[3])/2)
                    scx, scy = box_center(s_bbox)
                    s_face = min(s_faces, key=lambda f: (box_center(f.bbox)[0]-scx)**2 + (box_center(f.bbox)[1]-scy)**2)
                else:
                    s_face = max(s_faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
                t_emb = np.array(target_embeddings[t_id], dtype=np.float32)
                active_mapping[t_id] = {
                    'target_embedding': t_emb,
                    'source_face': s_face
                }

        if not active_mapping:
            # If no mapping, just copy the file
            shutil.copy(target_path, output_path)
            return 0

        def process_frame(frame: np.ndarray) -> np.ndarray:
            faces = self.app.get(frame)
            if not faces:
                return frame
            
            res = frame.copy()
            for face in faces:
                f_emb = self._get_embedding(face)
                
                # Find best matching target embedding
                best_t_id = None
                best_sim = -1.0
                
                for t_id, map_data in active_mapping.items():
                    sim = np.dot(f_emb, map_data['target_embedding'])
                    if sim > best_sim:
                        best_sim = sim
                        best_t_id = t_id
                
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
            return res

        frames_processed = 1
        if is_video:
            frames_processed = self._process_video(target_path, output_path, process_frame, export_profile=export_profile)
        else:
            img = cv2.imread(target_path)
            if img is not None:
                res = process_frame(img)
                cv2.imwrite(output_path, res)
        
        return frames_processed

    def _process_video(self, video_path: str, output_path: str, frame_processor, temp_dir='outputs/temp', export_profile='high') -> int:
        os.makedirs(temp_dir, exist_ok=True)
        audio_path = os.path.join(temp_dir, 'audio.aac')
        
        # Extract audio
        has_audio = False
        try:
            ffmpeg.input(video_path).output(audio_path, vn=None, acodec='copy').overwrite_output().run(quiet=True)
            has_audio = True
        except ffmpeg.Error:
            pass

        probe = ffmpeg.probe(video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width, height = int(video_info['width']), int(video_info['height'])
        
        process_in = (
            ffmpeg
            .input(video_path)
            .output('pipe:', format='rawvideo', pix_fmt='bgr24')
            .run_async(pipe_stdout=True, quiet=True)
        )

        process_out = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(width, height))
                        .output(
                os.path.join(temp_dir, 'video_no_audio.mp4'), 
                vcodec='libx264', 
                pix_fmt='yuv420p', 
                crf=14 if export_profile == 'lossless' else (28 if export_profile == 'web' else 18), 
                preset='veryslow' if export_profile == 'lossless' else ('fast' if export_profile == 'web' else 'slow')
            )
            .overwrite_output()
            .run_async(pipe_stdin=True, quiet=True)
        )

        in_bytes = width * height * 3
        frame_count = 0
        while True:
            in_data = process_in.stdout.read(in_bytes)
            if not in_data:
                break
            frame = np.frombuffer(in_data, np.uint8).reshape([height, width, 3])
            out_frame = frame_processor(frame)
            process_out.stdin.write(out_frame.tobytes())
            frame_count += 1

        process_out.stdin.close()
        process_in.wait()
        process_out.wait()

        # Remux
        video_no_audio = ffmpeg.input(os.path.join(temp_dir, 'video_no_audio.mp4'))
        if has_audio:
            audio = ffmpeg.input(audio_path)
            ffmpeg.output(video_no_audio, audio, output_path, vcodec='copy', acodec='aac').overwrite_output().run(quiet=True)
        else:
            ffmpeg.output(video_no_audio, output_path, vcodec='copy').overwrite_output().run(quiet=True)

        shutil.rmtree(temp_dir, ignore_errors=True)
        return frame_count

# Global instance
_multi_swapper_instance = None

def get_multi_swapper(use_cuda: bool = True):
    global _multi_swapper_instance
    current_use_cuda = getattr(_multi_swapper_instance, 'use_cuda', True) if _multi_swapper_instance else None
    
    if _multi_swapper_instance is None or current_use_cuda != use_cuda:
        _multi_swapper_instance = None
        import gc
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
            
        p = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_cuda else ['CPUExecutionProvider']
        _multi_swapper_instance = MultiFaceSwapper(providers=p)
        _multi_swapper_instance.use_cuda = use_cuda
    return _multi_swapper_instance
