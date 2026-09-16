import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

old_state = "const [history, setHistory] = useState<{filename: string, url: string, created_at: number, size: number}[]>([]);"
new_state = "const [history, setHistory] = useState<{filename: string, url: string, created_at: number, size: number, state?: string, task_id?: string, frames_processed?: number, params?: any}[]>([]);"
content = content.replace(old_state, new_state)

# Insert handleRetryJob function
old_fetchHistory = """  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/api/history`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data.history);
      }
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };"""

new_fetchHistory = """  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/api/history`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data.history);
      }
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  const handleRetryJob = async (job: any) => {
    if (!job.params || !job.params.source_path || !job.params.target_path) {
      alert("Missing job parameters for retry.");
      return;
    }
    
    setIsProcessing(true);
    setIsSidebarOpen(false); // Close sidebar
    
    try {
      const formData = new FormData();
      formData.append('source_paths', job.params.source_path);
      formData.append('target_paths', job.params.target_path);
      
      if (job.params.trim_start !== undefined && job.params.trim_start !== null) formData.append('trim_start', String(job.params.trim_start));
      if (job.params.trim_end !== undefined && job.params.trim_end !== null) formData.append('trim_end', String(job.params.trim_end));
      if (job.params.strength !== undefined && job.params.strength !== null) formData.append('strength', String(job.params.strength));
      if (job.params.enhance !== undefined && job.params.enhance !== null) formData.append('enhance', String(job.params.enhance));
      if (job.params.face_mapping) formData.append('face_mapping', job.params.face_mapping);
      if (job.params.mask_feather !== undefined && job.params.mask_feather !== null) formData.append('mask_feather', String(job.params.mask_feather));
      if (job.params.codec_quality) formData.append('codec_quality', job.params.codec_quality);
      if (job.params.output_format) formData.append('output_format', job.params.output_format);
      
      // Add skip_frames to resume
      if (job.frames_processed > 0) {
        formData.append('skip_frames', String(job.frames_processed));
      }
      
      const res = await fetch(`${API_URL}/api/swap`, {
        method: 'POST',
        body: formData
      });
      
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Swap request failed');
      }
      
      const data = await res.json();
      
      if (data.task_ids && data.task_ids.length > 0) {
        setJobs(prev => [...prev, ...data.task_ids.map((id: string) => ({
          id, state: 'QUEUED', progress: 0, statusMsg: 'Re-queued for resuming...', resultPath: null
        }))]);
      }
    } catch (err: any) {
      console.error(err);
      alert(`Retry Failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };"""

content = content.replace(old_fetchHistory, new_fetchHistory)

# Import RefreshCw
if "RefreshCw" not in content:
    content = content.replace("History,", "History, RefreshCw,")

# Replace Job History UI
old_history_map = """              history.map((job, idx) => (
                <div key={idx} className="p-4 bg-slate-50 border border-slate-200 rounded-xl hover:border-indigo-300 transition-colors group">
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-sm font-medium text-slate-700 truncate max-w-[200px]" title={job.filename}>
                      {job.filename}
                    </span>
                    <span className="text-xs text-slate-400">
                      {new Date(job.created_at * 1000).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between mt-4">
                    <span className="text-xs font-semibold text-slate-500 bg-slate-200 px-2 py-1 rounded">
                      {(job.size / (1024 * 1024)).toFixed(1)} MB
                    </span>
                    <a 
                      href={`${API_URL}${job.url}`}
                      download={job.filename}
                      className="text-xs font-medium text-white bg-indigo-600 px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-1.5 opacity-0 group-hover:opacity-100"
                    >
                      <Download size={14} /> Download
                    </a>
                  </div>
                </div>
              ))"""

new_history_map = """              history.map((job, idx) => (
                <div key={idx} className="p-4 bg-slate-50 border border-slate-200 rounded-xl hover:border-indigo-300 transition-colors group">
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-sm font-medium text-slate-700 truncate max-w-[200px]" title={job.filename}>
                      {job.filename}
                    </span>
                    <span className="text-xs text-slate-400">
                      {new Date(job.created_at * 1000).toLocaleDateString()}
                    </span>
                  </div>
                  
                  {job.state === 'FAILURE' && (
                     <div className="text-xs text-red-500 mb-2 font-medium bg-red-50 p-1.5 rounded inline-block">Failed at frame {job.frames_processed || 0}</div>
                  )}
                  {job.state === 'PROGRESS' && (
                     <div className="text-xs text-amber-500 mb-2 font-medium bg-amber-50 p-1.5 rounded inline-block">In Progress...</div>
                  )}
                  {job.state === 'QUEUED' && (
                     <div className="text-xs text-blue-500 mb-2 font-medium bg-blue-50 p-1.5 rounded inline-block">Queued...</div>
                  )}

                  <div className="flex items-center justify-between mt-4">
                    <span className="text-xs font-semibold text-slate-500 bg-slate-200 px-2 py-1 rounded">
                      {job.size > 0 ? (job.size / (1024 * 1024)).toFixed(1) + ' MB' : (job.state || 'UNKNOWN')}
                    </span>
                    
                    {job.state === 'FAILURE' ? (
                       <button 
                         onClick={() => handleRetryJob(job)}
                         className="text-xs font-medium text-white bg-amber-600 px-3 py-1.5 rounded-lg hover:bg-amber-700 transition-colors flex items-center gap-1.5"
                       >
                         <RefreshCw size={14} /> Retry/Resume
                       </button>
                    ) : job.state === 'SUCCESS' ? (
                       <a 
                         href={`${API_URL}${job.url}`}
                         download={job.filename}
                         className="text-xs font-medium text-white bg-indigo-600 px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-1.5 opacity-0 group-hover:opacity-100"
                       >
                         <Download size={14} /> Download
                       </a>
                    ) : null}
                  </div>
                </div>
              ))"""
              
content = content.replace(old_history_map, new_history_map)

with open('app/page.tsx', 'w') as f:
    f.write(content)
