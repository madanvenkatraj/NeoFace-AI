import sys

with open("backend/tasks.py", "r") as f:
    code = f.read()

get_orig = """        modifiers = data.get('modifiers', {})
        landmark_modifiers = data.get('landmark_modifiers', {})"""
get_new = """        modifiers = data.get('modifiers', {})
        landmark_modifiers = data.get('landmark_modifiers', {})
        source_bboxes = data.get('source_bboxes', {})"""
code = code.replace(get_orig, get_new)

call_orig = """        frames_processed = swapper_instance.process_media(
            target_path, 
            output_path, 
            target_to_source, 
            target_embeddings, 
            modifiers,
            landmark_modifiers,
            landmark_modifiers=landmark_modifiers,
            is_video=is_video,
            quality_mode=quality_mode,
            face_restoration=face_restoration,
            export_profile=export_profile
        )"""
call_new = """        frames_processed = swapper_instance.process_media(
            target_path, 
            output_path, 
            target_to_source, 
            target_embeddings, 
            modifiers,
            landmark_modifiers,
            source_bboxes,
            is_video=is_video,
            quality_mode=quality_mode,
            face_restoration=face_restoration,
            export_profile=export_profile
        )"""
code = code.replace(call_orig, call_new)

with open("backend/tasks.py", "w") as f:
    f.write(code)

print("Fixed tasks.py")
