import re

with open('backend/services/multi_face_swapper.py', 'r') as f:
    content = f.read()

old_global = "# Global instance\nswapper_instance = MultiFaceSwapper()"

new_global = """# Global instance
_multi_swapper_instance = None

def get_multi_swapper(use_cuda: bool = True):
    global _multi_swapper_instance
    current_use_cuda = getattr(_multi_swapper_instance, 'use_cuda', True) if _multi_swapper_instance else None
    
    if _multi_swapper_instance is None or current_use_cuda != use_cuda:
        _multi_swapper_instance = None
        import gc
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
            
        p = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_cuda else ['CPUExecutionProvider']
        _multi_swapper_instance = MultiFaceSwapper(providers=p)
        _multi_swapper_instance.use_cuda = use_cuda
    return _multi_swapper_instance"""

content = content.replace(old_global, new_global)

with open('backend/services/multi_face_swapper.py', 'w') as f:
    f.write(content)
