import sys

with open("backend/services/multi_face_swapper.py", "r") as f:
    code = f.read()

code = code.replace(
    "def process_media(self, target_path: str, output_path: str, target_to_source_mapping: Dict[str, str], target_embeddings: Dict[str, List[float]], modifiers: Dict[str, Dict[str, float]], is_video: bool = False, sim_threshold: float = 0.5) -> int:",
    "def process_media(self, target_path: str, output_path: str, target_to_source_mapping: Dict[str, str], target_embeddings: Dict[str, List[float]], modifiers: Dict[str, Dict[str, float]], is_video: bool = False, sim_threshold: float = 0.5, quality_mode: str = 'hd') -> int:"
)

code = code.replace(
    "            frames_processed = self._process_video(target_path, output_path, process_frame)",
    "            frames_processed = self._process_video(target_path, output_path, process_frame, quality_mode=quality_mode)"
)

code = code.replace(
    "def _process_video(self, video_path: str, output_path: str, frame_processor, temp_dir='outputs/temp') -> int:",
    "def _process_video(self, video_path: str, output_path: str, frame_processor, temp_dir='outputs/temp', quality_mode='hd') -> int:"
)

code = code.replace(
    "crf=23, preset='medium'",
    "crf=18 if quality_mode == 'hd' else 28, preset='slow' if quality_mode == 'hd' else 'fast'"
)

with open("backend/services/multi_face_swapper.py", "w") as f:
    f.write(code)
print("patched multi_face_swapper.py")
