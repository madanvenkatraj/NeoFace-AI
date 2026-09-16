import re

with open('backend/video_processor.py', 'r') as f:
    content = f.read()

# process_detect_faces
content = content.replace("def process_detect_faces(file_path: str):", "def process_detect_faces(file_path: str, use_cuda: bool = True):")
content = content.replace("    swapper = get_swapper()", "    swapper = get_swapper(use_cuda=use_cuda)")

# process_video_swap
content = content.replace("    skip_frames: int = 0", "    skip_frames: int = 0,\n    use_cuda: bool = True")
content = content.replace("    swapper = get_swapper()\n    source_img", "    swapper = get_swapper(use_cuda=use_cuda)\n    source_img")
content = content.replace("def process_detect_scenes(video_path: str, threshold: float = 0.3):", "def process_detect_scenes(video_path: str, threshold: float = 0.3, use_cuda: bool = True):")

with open('backend/video_processor.py', 'w') as f:
    f.write(content)
