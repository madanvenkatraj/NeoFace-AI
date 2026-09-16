import sys

# Patch tasks.py
with open("backend/tasks.py", "r") as f:
    tasks_code = f.read()

sig_orig = "def multi_face_swap_task(self, target_path: str, output_path: str, mapping_data: str, is_video: bool, use_cuda: bool = True, quality_mode: str = 'hd'):"
sig_rep = "def multi_face_swap_task(self, target_path: str, output_path: str, mapping_data: str, is_video: bool, use_cuda: bool = True, quality_mode: str = 'hd', face_restoration: bool = False, export_profile: str = 'high'):"
tasks_code = tasks_code.replace(sig_orig, sig_rep)

call_orig = """        frames_processed = swapper_instance.process_media(
            target_path, 
            output_path, 
            target_to_source, 
            target_embeddings,
            modifiers,
            is_video=is_video,
            quality_mode=quality_mode
        )"""
call_rep = """        frames_processed = swapper_instance.process_media(
            target_path, 
            output_path, 
            target_to_source, 
            target_embeddings,
            modifiers,
            is_video=is_video,
            quality_mode=quality_mode,
            face_restoration=face_restoration,
            export_profile=export_profile
        )"""
tasks_code = tasks_code.replace(call_orig, call_rep)

with open("backend/tasks.py", "w") as f:
    f.write(tasks_code)

# Patch main.py
with open("backend/main.py", "r") as f:
    main_code = f.read()

main_sig_orig = """@app.post("/api/target/swap")
async def multi_face_swap(
    target_path: str = Form(...),
    mapping_data: str = Form(...), # JSON string of mapping and embeddings
    is_video: bool = Form(...),
    use_cuda: bool = Form(True),
    quality_mode: str = Form("hd")
):"""
main_sig_rep = """@app.post("/api/target/swap")
async def multi_face_swap(
    target_path: str = Form(...),
    mapping_data: str = Form(...), # JSON string of mapping and embeddings
    is_video: bool = Form(...),
    use_cuda: bool = Form(True),
    quality_mode: str = Form("hd"),
    face_restoration: bool = Form(False),
    export_profile: str = Form("high")
):"""
main_code = main_code.replace(main_sig_orig, main_sig_rep)

task_call_orig = "    task = multi_face_swap_task.delay(target_path, output_path, mapping_data, is_video, use_cuda, quality_mode)"
task_call_rep = "    task = multi_face_swap_task.delay(target_path, output_path, mapping_data, is_video, use_cuda, quality_mode, face_restoration, export_profile)"
main_code = main_code.replace(task_call_orig, task_call_rep)

with open("backend/main.py", "w") as f:
    f.write(main_code)

print("Patched tasks.py and main.py")
