import re

with open('backend/video_processor.py', 'r') as f:
    content = f.read()

old_audio_block = """    # Extract audio
    if progress_callback:
        progress_callback(5, "Extracting audio", 0)
    audio_path = os.path.join(temp_dir, "audio.aac")
    
    in_kwargs = {}
    if trim_start is not None:
        in_kwargs['ss'] = trim_start
    if trim_end is not None and trim_start is not None:
        in_kwargs['t'] = trim_end - trim_start
    elif trim_end is not None:
        in_kwargs['to'] = trim_end
        
    try:
        ffmpeg.input(target_path, **in_kwargs).output(audio_path, vn=None, acodec='copy').overwrite_output().run(quiet=True)
        has_audio = True
    except ffmpeg.Error:
        has_audio = False

    # Get video info
    probe = ffmpeg.probe(target_path)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])"""

new_audio_block = """    # Get video info first to calculate framerate
    probe = ffmpeg.probe(target_path)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    
    fps_val = 30.0
    try:
        fps_val = eval(video_info.get('r_frame_rate', '30/1'))
    except:
        pass

    # Extract audio
    if progress_callback:
        progress_callback(5, "Extracting audio", 0)
    audio_path = os.path.join(temp_dir, "audio.aac")
    
    in_kwargs = {}
    
    adjusted_trim_start = trim_start or 0.0
    if skip_frames > 0:
        adjusted_trim_start += (skip_frames / fps_val)
        
    if adjusted_trim_start > 0:
        in_kwargs['ss'] = adjusted_trim_start
        
    if trim_end is not None:
        in_kwargs['to'] = trim_end
        
    try:
        ffmpeg.input(target_path, **in_kwargs).output(audio_path, vn=None, acodec='copy').overwrite_output().run(quiet=True)
        has_audio = True
    except ffmpeg.Error:
        has_audio = False"""

content = content.replace(old_audio_block, new_audio_block)

with open('backend/video_processor.py', 'w') as f:
    f.write(content)
