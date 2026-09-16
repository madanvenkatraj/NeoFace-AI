import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

# 1. Update SourceMapping interface
code = code.replace("  uploadedPath: string;\n}", "  uploadedPath: string;\n  sourceBbox?: number[];\n}")

# 2. Add State for Source Selection Modal
state_code = """
  const [sourceSelectionModal, setSourceSelectionModal] = useState<{
    targetFaceId: string;
    sourcePath: string;
    previewUrl: string;
    faces: any[];
  } | null>(null);
  const [sourceModalLoading, setSourceModalLoading] = useState<string | null>(null);
"""
# Insert after `const [error, setError] = useState<string | null>(null);`
code = code.replace("  const [error, setError] = useState<string | null>(null);", "  const [error, setError] = useState<string | null>(null);" + state_code)

# 3. Update handleSourceUpload to call /api/target/detect
orig_handle_upload = """  const handleSourceUpload = async (faceId: string, file: File) => {
    const previewUrl = URL.createObjectURL(file);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      // Optimistic update
      setFaceMappings(prev => ({ ...prev, [faceId]: { previewUrl, uploadedPath: '' } }));
      
      const res = await fetch(`${API_URL}/api/upload`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error('Upload failed');
      const data = await res.json();
      
      setFaceMappings(prev => ({
        ...prev,
        [faceId]: { previewUrl, uploadedPath: data.path }
      }));
    } catch (err) {
      console.error(err);
      // Remove optimistic update if it failed
      setFaceMappings(prev => {
        const next = { ...prev };
        delete next[faceId];
        return next;
      });
    }
  };"""

new_handle_upload = """  const handleSourceUpload = async (faceId: string, file: File) => {
    setSourceModalLoading(faceId);
    const previewUrl = URL.createObjectURL(file);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('use_cuda', getUseCuda().toString());
    
    try {
      // Use the detect endpoint to find all faces in the source image
      const res = await fetch(`${API_URL}/api/target/detect`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error('Detection failed');
      const data = await res.json();
      
      if (!data.faces || data.faces.length === 0) {
        alert("No faces detected in the uploaded image.");
        setSourceModalLoading(null);
        return;
      }
      
      if (data.faces.length === 1) {
        // If only 1 face, auto select it
        setFaceMappings(prev => ({
          ...prev,
          [faceId]: { previewUrl, uploadedPath: data.target_path, sourceBbox: data.faces[0].bbox }
        }));
      } else {
        // Multiple faces found, open selection modal
        setSourceSelectionModal({
          targetFaceId: faceId,
          sourcePath: data.target_path,
          previewUrl,
          faces: data.faces
        });
      }
    } catch (err) {
      console.error(err);
      alert("Failed to process source image");
    } finally {
      setSourceModalLoading(null);
    }
  };"""
code = code.replace(orig_handle_upload, new_handle_upload)


# 4. In `startSwap`, build source_bboxes dict
orig_start_swap_dict = """      const embeddingsDict: Record<string, number[]> = {};
      const modifiersDict: Record<string, { expansion: number, erosion: number }> = {};"""
new_start_swap_dict = """      const embeddingsDict: Record<string, number[]> = {};
      const modifiersDict: Record<string, { expansion: number, erosion: number }> = {};
      const sourceBboxesDict: Record<string, number[]> = {};"""
code = code.replace(orig_start_swap_dict, new_start_swap_dict)

orig_start_swap_loop = """          modifiersDict[f.face_id] = {
            expansion: (maskModifiers[f.face_id]?.expansion || 0) / 100,
            erosion: (maskModifiers[f.face_id]?.erosion || 0) / 100
          };"""
new_start_swap_loop = """          modifiersDict[f.face_id] = {
            expansion: (maskModifiers[f.face_id]?.expansion || 0) / 100,
            erosion: (maskModifiers[f.face_id]?.erosion || 0) / 100
          };
          if (faceMappings[f.face_id].sourceBbox) {
             sourceBboxesDict[f.face_id] = faceMappings[f.face_id].sourceBbox!;
          }"""
code = code.replace(orig_start_swap_loop, new_start_swap_loop)

orig_start_swap_append = """      formData.append('modifiers', JSON.stringify(modifiersDict));"""
new_start_swap_append = """      formData.append('modifiers', JSON.stringify(modifiersDict));
      formData.append('source_bboxes', JSON.stringify(sourceBboxesDict));"""
code = code.replace(orig_start_swap_append, new_start_swap_append)


# 5. Render the SourceSelectionModal at the end of FaceMappingStudio
source_modal_jsx = """
      {sourceSelectionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl w-full max-w-4xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <div>
                <h3 className="text-xl font-bold text-slate-800">Multiple Faces Detected</h3>
                <p className="text-sm text-slate-500 mt-1">Select the specific face you want to use as the source.</p>
              </div>
              <button 
                onClick={() => setSourceSelectionModal(null)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1 flex flex-col items-center">
              <div className="relative inline-block border-2 border-slate-200 rounded-xl overflow-hidden bg-slate-100">
                <img 
                  id="source-modal-img"
                  src={sourceSelectionModal.previewUrl} 
                  alt="Source" 
                  className="max-h-[60vh] max-w-full object-contain block"
                />
                
                {sourceSelectionModal.faces.map((face, idx) => {
                  return (
                    <div
                      key={face.face_id}
                      onClick={() => {
                        setFaceMappings(prev => ({
                          ...prev,
                          [sourceSelectionModal.targetFaceId]: {
                            previewUrl: sourceSelectionModal.previewUrl,
                            uploadedPath: sourceSelectionModal.sourcePath,
                            sourceBbox: face.bbox
                          }
                        }));
                        setSourceSelectionModal(null);
                      }}
                      className="absolute border-4 border-emerald-500 cursor-pointer hover:bg-emerald-500/20 transition-all flex items-center justify-center group"
                      style={{
                        left: `${(face.bbox[0] / (document.getElementById('source-modal-img') as HTMLImageElement)?.naturalWidth || 1) * 100}%`,
                        top: `${(face.bbox[1] / (document.getElementById('source-modal-img') as HTMLImageElement)?.naturalHeight || 1) * 100}%`,
                        width: `${((face.bbox[2] - face.bbox[0]) / (document.getElementById('source-modal-img') as HTMLImageElement)?.naturalWidth || 1) * 100}%`,
                        height: `${((face.bbox[3] - face.bbox[1]) / (document.getElementById('source-modal-img') as HTMLImageElement)?.naturalHeight || 1) * 100}%`,
                      }}
                    >
                      <div className="absolute -top-10 bg-emerald-600 text-white font-bold px-3 py-1 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                        Select Face {idx + 1}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            
            <div className="p-6 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
              <button 
                onClick={() => setSourceSelectionModal(null)}
                className="px-6 py-2.5 rounded-xl font-bold text-slate-600 hover:bg-slate-200 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
"""
# Insert before final closing tag of FaceMappingStudio
code = code.replace("    </div>\n  );\n}", source_modal_jsx + "\n    </div>\n  );\n}")

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)

print("Patched FaceMappingStudio for Source Selection")
