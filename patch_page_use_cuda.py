import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# Add useCuda state
old_state = """  const [autoSpindown, setAutoSpindown] = useState<boolean>(false);
  
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setAutoSpindown(localStorage.getItem('neoFace_autoSpindown') === 'true');
    }
  }, []);"""

new_state = """  const [autoSpindown, setAutoSpindown] = useState<boolean>(false);
  const [useCuda, setUseCuda] = useState<boolean>(true);
  const [gpuActive, setGpuActive] = useState<boolean>(false);
  
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setAutoSpindown(localStorage.getItem('neoFace_autoSpindown') === 'true');
      const savedCuda = localStorage.getItem('neoFace_useCuda');
      if (savedCuda !== null) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setUseCuda(savedCuda === 'true');
      }
    }
    
    // Check GPU metrics
    const checkGpu = async () => {
       try {
         const res = await fetch(`${API_URL}/api/system/metrics`);
         if (res.ok) {
           const data = await res.json();
           if (data.available) {
             setGpuActive(true);
           } else {
             setGpuActive(false);
           }
         }
       } catch (err) {}
    };
    checkGpu();
  }, [API_URL]);
  
  useEffect(() => {
    localStorage.setItem('neoFace_useCuda', useCuda.toString());
  }, [useCuda]);"""
content = content.replace(old_state, new_state)

# Add useCuda to formData for handleRetryJob
old_retry = """      if (job.frames_processed > 0) {
        formData.append('skip_frames', String(job.frames_processed));
      }
      
      const res = await fetch(`${API_URL}/api/swap`, {"""

new_retry = """      if (job.frames_processed > 0) {
        formData.append('skip_frames', String(job.frames_processed));
      }
      formData.append('use_cuda', useCuda.toString());
      
      const res = await fetch(`${API_URL}/api/swap`, {"""
content = content.replace(old_retry, new_retry)

# Add useCuda to handleDetectFaces
old_detect = """    formData.append('file', file);
    
    try {
      const res = await fetch(`${API_URL}/api/detect`, {"""

new_detect = """    formData.append('file', file);
    formData.append('use_cuda', useCuda.toString());
    
    try {
      const res = await fetch(`${API_URL}/api/detect`, {"""
content = content.replace(old_detect, new_detect)

# Add useCuda to handleSwap
old_swap = """      if (Object.keys(faceMapping).length > 0) {
        formData.append('face_mapping', JSON.stringify(faceMapping));
      }
      
      const res = await fetch(`${API_URL}/api/swap`, {"""

new_swap = """      if (Object.keys(faceMapping).length > 0) {
        formData.append('face_mapping', JSON.stringify(faceMapping));
      }
      formData.append('use_cuda', useCuda.toString());
      
      const res = await fetch(`${API_URL}/api/swap`, {"""
content = content.replace(old_swap, new_swap)

with open('app/page.tsx', 'w') as f:
    f.write(content)
