with open('components/NeoFaceStudio.tsx', 'r') as f:
    lines = f.readlines()

content = "".join(lines)

import re

# find the bad effects block
effects = """  // Tab Sync (Processing History)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'neoface_batch_jobs' && e.newValue) {
        try {
          setBatchJobsEx(JSON.parse(e.newValue));
        } catch(err) {}
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  useEffect(() => {
    localStorage.setItem('neoface_batch_jobs', JSON.stringify(batchJobsEx));
  }, [batchJobsEx]);
"""

# remove it
if effects in content:
    content = content.replace(effects, "")

# insert it after batchJobsEx
target_decl = """  // Extend Batch Jobs
  const [batchJobsEx, setBatchJobsEx] = useState([
    { id: 'b1', name: 'Scene_01_Interview.mp4', status: 'Processing', progress: 45, eta: '2m 14s', gpu: '85% VRAM' }, 
    { id: 'b2', name: 'Scene_02_B-Roll.mp4', status: 'Queued', progress: 0, eta: 'Pending', gpu: '-' }
  ]);"""

if target_decl in content:
    content = content.replace(target_decl, target_decl + "\n\n" + effects)

with open('components/NeoFaceStudio.tsx', 'w') as f:
    f.write(content)
