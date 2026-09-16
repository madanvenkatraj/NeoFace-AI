import sys

with open("backend/tasks.py", "r") as f:
    code = f.read()

code = code.replace(
    "def multi_face_swap_task(self, target_path: str, output_path: str, mapping_data: str, is_video: bool, use_cuda: bool = True):",
    "def multi_face_swap_task(self, target_path: str, output_path: str, mapping_data: str, is_video: bool, use_cuda: bool = True, quality_mode: str = 'hd'):"
)

code = code.replace(
    """        frames_processed = swapper_instance.process_media(
            target_path, 
            output_path, 
            target_to_source, 
            target_embeddings, 
            modifiers,
            is_video=is_video
        )""",
    """        frames_processed = swapper_instance.process_media(
            target_path, 
            output_path, 
            target_to_source, 
            target_embeddings, 
            modifiers,
            is_video=is_video,
            quality_mode=quality_mode
        )"""
)

with open("backend/tasks.py", "w") as f:
    f.write(code)
print("patched tasks.py")
