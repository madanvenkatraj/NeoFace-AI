import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# 1. Update state definition
content = content.replace(
    "const [target, setTarget] = useState<FileState>({ file: null, previewUrl: null, uploadedPath: null, faces: null, imageSize: null });",
    "const [targets, setTargets] = useState<FileState[]>([]);\n  const target = targets[0] || { file: null, previewUrl: null, uploadedPath: null, faces: null, imageSize: null };"
)

# 2. Update handleUpload
old_handle_upload_target_1 = "setTarget({ file, previewUrl, uploadedPath: null, faces: null, imageSize: null });"
new_handle_upload_target_1 = "setTargets(prev => [...prev, { file, previewUrl, uploadedPath: null, faces: null, imageSize: null }]);"
content = content.replace(old_handle_upload_target_1, new_handle_upload_target_1)

old_handle_upload_target_2 = "setTarget(prev => ({ ...prev, uploadedPath: data.path }));"
new_handle_upload_target_2 = "setTargets(prev => prev.map(t => t.previewUrl === previewUrl ? { ...t, uploadedPath: data.path } : t));"
content = content.replace(old_handle_upload_target_2, new_handle_upload_target_2)

old_handle_upload_target_3 = "setTarget(prev => ({ ...prev, faces: detectData.faces, imageSize: { width: detectData.width, height: detectData.height } }));"
new_handle_upload_target_3 = "setTargets(prev => prev.map(t => t.previewUrl === previewUrl ? { ...t, faces: detectData.faces, imageSize: { width: detectData.width, height: detectData.height } } : t));"
content = content.replace(old_handle_upload_target_3, new_handle_upload_target_3)

old_handle_upload_target_4 = "setTarget((prev) => ({ ...prev, uploadedPath: 'mock/path/target.mp4' }));"
new_handle_upload_target_4 = "setTargets(prev => prev.map(t => t.previewUrl === previewUrl ? { ...t, uploadedPath: 'mock/path/target.mp4' } : t));"
content = content.replace(old_handle_upload_target_4, new_handle_upload_target_4)

old_handle_upload_target_5 = "setTarget({ file: null, previewUrl: null, uploadedPath: null, faces: null, imageSize: null });"
new_handle_upload_target_5 = "setTargets(prev => prev.filter(t => t.previewUrl !== previewUrl));"
content = content.replace(old_handle_upload_target_5, new_handle_upload_target_5)

# 3. Update handleUrlUpload
old_handle_url_target_1 = "setTarget({ file: null, previewUrl: url, uploadedPath: null, faces: null, imageSize: null });"
new_handle_url_target_1 = "setTargets(prev => [...prev, { file: null, previewUrl: url, uploadedPath: null, faces: null, imageSize: null }]);"
content = content.replace(old_handle_url_target_1, new_handle_url_target_1)

# Note: handleUrlUpload also has target_2, target_3, etc. They are identical so replacing them should work generally.

# 4. Update onDropTarget
old_ondrop_target = "if (acceptedFiles.length > 0) handleUpload(acceptedFiles[0], 'target');"
new_ondrop_target = "acceptedFiles.forEach(f => handleUpload(f, 'target'));"
content = content.replace(old_ondrop_target, new_ondrop_target)

# 5. Update dropzone config for target
old_dropzone = "accept: { 'video/*': ['.mp4', '.mov', '.avi'], 'image/*': ['.jpeg', '.jpg', '.png'] },\n    maxFiles: 1"
new_dropzone = "accept: { 'video/*': ['.mp4', '.mov', '.avi'], 'image/*': ['.jpeg', '.jpg', '.png'] }\n    // batch mode allowed"
content = content.replace(old_dropzone, new_dropzone)

# 6. Update startSwap to pass all target paths
old_start_swap = "formData.append('target_path', target.uploadedPath);"
new_start_swap = "targets.forEach(t => { if(t.uploadedPath) formData.append('target_paths', t.uploadedPath) });\n      formData.append('target_path', target.uploadedPath); // keep for backward compatibility"
content = content.replace(old_start_swap, new_start_swap)

# 7. Update UI clear target
old_clear_target = "onClick={() => setTarget({ file: null, previewUrl: null, uploadedPath: null, faces: null, imageSize: null })}"
new_clear_target = "onClick={() => setTargets([])}"
content = content.replace(old_clear_target, new_clear_target)

# 8. Add visual indication for multiple targets in UI
# Find the text "Drag & drop video or photo" and add something below it or just let the user know.
# Let's change the header or something if targets > 1
old_preview = "src={target.previewUrl} \n                      controls={!activeTrimHandle}"
new_preview = "src={target.previewUrl || ''} \n                      controls={!activeTrimHandle}"
content = content.replace(old_preview, new_preview)

with open('app/page.tsx', 'w') as f:
    f.write(content)
