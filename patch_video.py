import re

with open('backend/video_processor.py', 'r') as f:
    content = f.read()

old_def = """def process_video_swap(
    source_path: str, 
    target_path: str, 
    output_path: str, 
    progress_callback: Optional[Callable[[int, str], None]] = None,
    trim_start: Optional[float] = None,
    trim_end: Optional[float] = None,
    strength: float = 1.0,
    enhance: bool = True,
    face_mapping: Optional[str] = None,
    mask_feather: float = 0.5,
    codec_quality: str = 'medium'
):"""
new_def = """def process_video_swap(
    source_path: str, 
    target_path: str, 
    output_path: str, 
    progress_callback: Optional[Callable[[int, str, int], None]] = None,
    trim_start: Optional[float] = None,
    trim_end: Optional[float] = None,
    strength: float = 1.0,
    enhance: bool = True,
    face_mapping: Optional[str] = None,
    mask_feather: float = 0.5,
    codec_quality: str = 'medium',
    skip_frames: int = 0
):"""
content = content.replace(old_def, new_def)

# Fix progress_callback calls that only pass 2 args to pass 3 args where needed, 
# although we can just safely update the one in the loop.
old_loop = """    while True:
        in_frame = process_in.stdout.read(in_bytes)
        if not in_frame:
            break

        frame = np.frombuffer(in_frame, np.uint8).reshape([height, width, 3])
        
        # Swap
        if trackers:
            swapped_frame = swapper.swap_faces_tracked(trackers, frame, enhance=enhance, strength=strength, mask_feather=mask_feather)
        else:
            swapped_frame = swapper.swap_face(source_img, frame, enhance=enhance, strength=strength, mask_feather=mask_feather)
            
        process_out.stdin.write(swapped_frame.tobytes())
        
        frame_idx += 1
        if progress_callback and frame_idx % 30 == 0:
            pct = 10 + min(80, int((frame_idx / total_frames) * 80)) if total_frames > 0 else 10
            progress_callback(pct, f"Swapped frame {frame_idx}/{total_frames if total_frames > 0 else 'Unknown'}")"""

new_loop = """    while True:
        in_frame = process_in.stdout.read(in_bytes)
        if not in_frame:
            break

        if frame_idx < skip_frames:
            frame_idx += 1
            if progress_callback and frame_idx % 30 == 0:
                pct = min(10, int((frame_idx / skip_frames) * 10)) if skip_frames > 0 else 10
                progress_callback(pct, f"Skipping to frame {frame_idx}/{skip_frames}...", frame_idx)
            continue

        frame = np.frombuffer(in_frame, np.uint8).reshape([height, width, 3])
        
        # Swap
        if trackers:
            swapped_frame = swapper.swap_faces_tracked(trackers, frame, enhance=enhance, strength=strength, mask_feather=mask_feather)
        else:
            swapped_frame = swapper.swap_face(source_img, frame, enhance=enhance, strength=strength, mask_feather=mask_feather)
            
        process_out.stdin.write(swapped_frame.tobytes())
        
        frame_idx += 1
        if progress_callback and frame_idx % 30 == 0:
            pct = 10 + min(80, int((frame_idx / total_frames) * 80)) if total_frames > 0 else 10
            progress_callback(pct, f"Swapped frame {frame_idx}/{total_frames if total_frames > 0 else 'Unknown'}", frame_idx)"""

content = content.replace(old_loop, new_loop)

# Fix progress_callback(0, ...) -> progress_callback(0, ..., 0)
content = content.replace("progress_callback(0, \"Initializing models\")", "progress_callback(0, \"Initializing models\", 0)")
content = content.replace("progress_callback(5, \"Extracting audio\")", "progress_callback(5, \"Extracting audio\", 0)")
content = content.replace("progress_callback(10, \"Extracting frames\")", "progress_callback(10, \"Extracting frames\", 0)")
content = content.replace("progress_callback(95, \"Remuxing audio\")", "progress_callback(95, \"Remuxing audio\", frame_idx)")
content = content.replace("progress_callback(100, \"Completed\")", "progress_callback(100, \"Completed\", frame_idx)")

with open('backend/video_processor.py', 'w') as f:
    f.write(content)
