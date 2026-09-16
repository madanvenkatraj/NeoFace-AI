import sys

with open("backend/main.py", "r") as f:
    code = f.read()

old_func = """@app.post("/api/target/swap")
async def multi_face_swap(
    target_path: str = Form(...),
    mapping_data: str = Form(...), # JSON string of mapping and embeddings
    is_video: bool = Form(...),
    use_cuda: bool = Form(True)
):"""

new_func = """@app.post("/api/target/swap")
async def multi_face_swap(
    target_path: str = Form(...),
    mapping_data: str = Form(...), # JSON string of mapping and embeddings
    is_video: bool = Form(...),
    use_cuda: bool = Form(True),
    quality_mode: str = Form("hd")
):"""

code = code.replace(old_func, new_func)

code = code.replace(
    "    task = multi_face_swap_task.delay(target_path, output_path, mapping_data, is_video, use_cuda)",
    "    task = multi_face_swap_task.delay(target_path, output_path, mapping_data, is_video, use_cuda, quality_mode)"
)

with open("backend/main.py", "w") as f:
    f.write(code)
print("patched main.py")
