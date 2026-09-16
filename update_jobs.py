with open('app/page.tsx', 'r') as f:
    content = f.read()

# Update job state type
old_jobs_type = "const [jobs, setJobs] = useState<{id: string, progress: number, statusMsg: string, state: string, resultPath?: string, error?: string, metrics?: any}[]>([]);"
new_jobs_type = "const [jobs, setJobs] = useState<{id: string, progress: number, statusMsg: string, state: string, resultPath?: string, error?: string, metrics?: any, targetIdx?: number}[]>([]);"
content = content.replace(old_jobs_type, new_jobs_type)

# Update initialJobs creation
old_initial_jobs = "const initialJobs = data.task_ids.map((id: string) => ({ id, progress: 0, statusMsg: 'Queued', state: 'QUEUED' }));"
new_initial_jobs = "const initialJobs = data.task_ids.map((id: string, idx: number) => ({ id, progress: 0, statusMsg: 'Queued', state: 'QUEUED', targetIdx: Math.floor(idx / uploadedSourcePaths.length) }));"
content = content.replace(old_initial_jobs, new_initial_jobs)

# Update UI mapping in results
# Find beforeSrc={target.previewUrl!} and afterSrc=...
old_beforeSrc = "beforeSrc={target.previewUrl!}"
new_beforeSrc = "beforeSrc={targets[job.targetIdx || 0]?.previewUrl || ''}"
content = content.replace(old_beforeSrc, new_beforeSrc)

old_isVideo = "isVideo={target.file?.type.startsWith('video') || false}"
new_isVideo = "isVideo={targets[job.targetIdx || 0]?.file?.type.startsWith('video') || false}"
content = content.replace(old_isVideo, new_isVideo)

with open('app/page.tsx', 'w') as f:
    f.write(content)
