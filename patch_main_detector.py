import re

with open('backend/main.py', 'r') as f:
    content = f.read()

# detect_target_faces
old_detect_def = """async def detect_target_faces(file: UploadFile = File(...)):
    from services.multi_face_detector import detector_instance"""
new_detect_def = """async def detect_target_faces(file: UploadFile = File(...), use_cuda: bool = Form(True)):
    from services.multi_face_detector import get_detector
    detector_instance = get_detector(use_cuda=use_cuda)"""
content = content.replace(old_detect_def, new_detect_def)

# automap_source_faces
old_automap_def = """async def automap_source_faces(
    file: UploadFile = File(...),
    target_embeddings: str = Form(...) # JSON string { target_face_id: [emb...] }
):
    import json
    from services.multi_face_detector import detector_instance"""

new_automap_def = """async def automap_source_faces(
    file: UploadFile = File(...),
    target_embeddings: str = Form(...), # JSON string { target_face_id: [emb...] }
    use_cuda: bool = Form(True)
):
    import json
    from services.multi_face_detector import get_detector
    detector_instance = get_detector(use_cuda=use_cuda)"""
content = content.replace(old_automap_def, new_automap_def)

# And one more: the standard detect faces
old_detect_faces = """@app.post("/api/detect")
async def detect_faces(file: UploadFile = File(...)):
    ext = file.filename.split('.')[-1]
    temp_path = os.path.join(UPLOAD_DIR, f"detect_{uuid.uuid4()}.{ext}")
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        from video_processor import process_detect_faces
        result = process_detect_faces(temp_path)"""

new_detect_faces = """@app.post("/api/detect")
async def detect_faces(file: UploadFile = File(...), use_cuda: bool = Form(True)):
    ext = file.filename.split('.')[-1]
    temp_path = os.path.join(UPLOAD_DIR, f"detect_{uuid.uuid4()}.{ext}")
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        from video_processor import process_detect_faces
        result = process_detect_faces(temp_path, use_cuda=use_cuda)"""
content = content.replace(old_detect_faces, new_detect_faces)

with open('backend/main.py', 'w') as f:
    f.write(content)
