import re

with open('backend/main.py', 'r') as f:
    content = f.read()

# start_swap endpoint
old_start_swap = """    output_format: str = Form("mp4"),
    codec_quality: str = Form("medium"),
    skip_frames: int = Form(0)
):"""

new_start_swap = """    output_format: str = Form("mp4"),
    codec_quality: str = Form("medium"),
    skip_frames: int = Form(0),
    use_cuda: bool = Form(True)
):"""
content = content.replace(old_start_swap, new_start_swap)

old_swap_delay = "task = swap_video_task.delay(sp, tp, output_path, trim_start, trim_end, strength, enhance, face_mapping, mask_feather, codec_quality, skip_frames)"
new_swap_delay = "task = swap_video_task.delay(sp, tp, output_path, trim_start, trim_end, strength, enhance, face_mapping, mask_feather, codec_quality, skip_frames, use_cuda)"
content = content.replace(old_swap_delay, new_swap_delay)

# multi_face_swap endpoint
old_multi_swap = """async def multi_face_swap(
    target_path: str = Form(...),
    mapping_data: str = Form(...), # JSON string of mapping and embeddings
    is_video: bool = Form(...)
):"""

new_multi_swap = """async def multi_face_swap(
    target_path: str = Form(...),
    mapping_data: str = Form(...), # JSON string of mapping and embeddings
    is_video: bool = Form(...),
    use_cuda: bool = Form(True)
):"""
content = content.replace(old_multi_swap, new_multi_swap)

old_multi_delay = "task = multi_face_swap_task.delay(target_path, output_path, mapping_data, is_video)"
new_multi_delay = "task = multi_face_swap_task.delay(target_path, output_path, mapping_data, is_video, use_cuda)"
content = content.replace(old_multi_delay, new_multi_delay)

with open('backend/main.py', 'w') as f:
    f.write(content)
