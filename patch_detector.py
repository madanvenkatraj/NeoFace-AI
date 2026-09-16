import re

with open('backend/services/multi_face_detector.py', 'r') as f:
    content = f.read()

old_global = "# Global instance\ndetector_instance = MultiFaceDetector()"
new_global = """# Global instance
_detector_instance = None

def get_detector(use_cuda: bool = True):
    global _detector_instance
    current_use_cuda = getattr(_detector_instance, 'use_cuda', True) if _detector_instance else None
    
    if _detector_instance is None or current_use_cuda != use_cuda:
        _detector_instance = None
        import gc
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
            
        p = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_cuda else ['CPUExecutionProvider']
        _detector_instance = MultiFaceDetector(providers=p)
        _detector_instance.use_cuda = use_cuda
    return _detector_instance"""

content = content.replace(old_global, new_global)

with open('backend/services/multi_face_detector.py', 'w') as f:
    f.write(content)
