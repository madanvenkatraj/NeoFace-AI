import re

with open('backend/video_processor.py', 'r') as f:
    content = f.read()

# Change FaceSwapper init
old_init = """class FaceSwapper:
    def __init__(self, model_dir: str = "../models"):
        self.app = FaceAnalysis(name='buffalo_l', root=model_dir, providers=providers)
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
        swapper_path = os.path.join(model_dir, 'inswapper_128.onnx')
        self.swapper = insightface.model_zoo.get_model(swapper_path, download=False, download_zip=False)"""

new_init = """class FaceSwapper:
    def __init__(self, model_dir: str = "../models", providers: list = ['CUDAExecutionProvider', 'CPUExecutionProvider']):
        self.app = FaceAnalysis(name='buffalo_l', root=model_dir, providers=providers)
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
        swapper_path = os.path.join(model_dir, 'inswapper_128.onnx')
        self.swapper = insightface.model_zoo.get_model(swapper_path, download=False, download_zip=False)"""
content = content.replace(old_init, new_init)

# Change get_swapper
old_get_swapper = """def get_swapper():
    global _swapper_instance
    if _swapper_instance is None:
        _swapper_instance = FaceSwapper(model_dir="/app/models")
    return _swapper_instance"""

new_get_swapper = """def get_swapper(use_cuda: bool = True):
    global _swapper_instance
    
    current_use_cuda = getattr(_swapper_instance, 'use_cuda', True) if _swapper_instance else None
    
    if _swapper_instance is None or current_use_cuda != use_cuda:
        _swapper_instance = None
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
            
        p = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_cuda else ['CPUExecutionProvider']
        _swapper_instance = FaceSwapper(model_dir="/app/models", providers=p)
        _swapper_instance.use_cuda = use_cuda
    return _swapper_instance"""
content = content.replace(old_get_swapper, new_get_swapper)

with open('backend/video_processor.py', 'w') as f:
    f.write(content)
