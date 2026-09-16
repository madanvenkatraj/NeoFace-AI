import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

# Add states
state_insert = "  const [qualityMode, setQualityMode] = useState<'hd' | 'fast'>('hd');"
state_replacement = """  const [qualityMode, setQualityMode] = useState<'hd' | 'fast'>('hd');
  const [faceRestoration, setFaceRestoration] = useState(false);
  const [exportProfile, setExportProfile] = useState<'web' | 'high' | 'lossless'>('high');"""
code = code.replace(state_insert, state_replacement)

# Add form data
form_insert = "      formData.append('quality_mode', qualityMode);"
form_replacement = """      formData.append('quality_mode', qualityMode);
      formData.append('face_restoration', faceRestoration.toString());
      formData.append('export_profile', exportProfile);"""
code = code.replace(form_insert, form_replacement)

# UI Replacement
ui_insert = """          <div className="pt-6 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="flex items-center gap-2 border border-slate-200 bg-white p-1 rounded-xl">
                <button 
                  onClick={() => setQualityMode('fast')}
                  className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${qualityMode === 'fast' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50'}`}
                >
                  ⚡ Fast
                </button>
                <button 
                  onClick={() => setQualityMode('hd')}
                  className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${qualityMode === 'hd' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50'}`}
                >
                  ✨ High Quality (HD)
                </button>
              </div>
              <div className="text-sm font-medium text-slate-600">
                <span className="text-indigo-600 font-bold">{Object.keys(faceMappings).length}</span> of {detectedFaces.length} faces mapped
              </div>
            </div>
            
            <button
              onClick={startSwap}
              disabled={Object.keys(faceMappings).length === 0 || !!jobId}
              className="w-full md:w-auto px-10 py-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:text-slate-500 text-white rounded-xl font-bold text-lg shadow-md transition-all flex items-center justify-center gap-2"
            >
              {jobId ? <Loader2 className="animate-spin" size={24} /> : <Play size={24} />}
              {jobId ? "Processing Multi-Swap..." : "Start Multi-Swap"}
            </button>
          </div>"""

ui_replacement = """          <div className="pt-6 border-t border-slate-100 flex flex-col gap-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-slate-50 p-6 rounded-2xl border border-slate-200">
              <div className="flex flex-col gap-3">
                <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                  <Wand2 size={18} className="text-indigo-500" />
                  Post-Processing
                </h3>
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className={`w-10 h-6 rounded-full transition-colors flex items-center px-1 ${faceRestoration ? 'bg-indigo-500' : 'bg-slate-300'}`}>
                    <div className={`w-4 h-4 bg-white rounded-full transition-transform ${faceRestoration ? 'translate-x-4' : 'translate-x-0'}`} />
                  </div>
                  <input type="checkbox" className="hidden" checked={faceRestoration} onChange={(e) => setFaceRestoration(e.target.checked)} />
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-slate-700 group-hover:text-indigo-600 transition-colors">AI Face Restoration</span>
                    <span className="text-xs text-slate-500">Enhance clarity and detail of swapped faces using CodeFormer pass</span>
                  </div>
                </label>
              </div>
              
              <div className="flex flex-col gap-3">
                <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                  <Film size={18} className="text-indigo-500" />
                  Export Profile
                </h3>
                <div className="flex bg-white border border-slate-200 rounded-xl p-1 shadow-sm">
                  <button 
                    onClick={() => setExportProfile('web')}
                    className={`flex-1 px-3 py-2 rounded-lg text-xs font-bold transition-all ${exportProfile === 'web' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50'}`}
                  >
                    Web Optimized
                  </button>
                  <button 
                    onClick={() => setExportProfile('high')}
                    className={`flex-1 px-3 py-2 rounded-lg text-xs font-bold transition-all ${exportProfile === 'high' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50'}`}
                  >
                    High Quality
                  </button>
                  <button 
                    onClick={() => setExportProfile('lossless')}
                    className={`flex-1 px-3 py-2 rounded-lg text-xs font-bold transition-all ${exportProfile === 'lossless' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50'}`}
                  >
                    Lossless
                  </button>
                </div>
              </div>
            </div>

            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
              <div className="text-sm font-medium text-slate-600">
                <span className="text-indigo-600 font-bold">{Object.keys(faceMappings).length}</span> of {detectedFaces.length} faces mapped
              </div>
              
              <button
                onClick={startSwap}
                disabled={Object.keys(faceMappings).length === 0 || !!jobId}
                className="w-full md:w-auto px-10 py-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:text-slate-500 text-white rounded-xl font-bold text-lg shadow-md transition-all flex items-center justify-center gap-2"
              >
                {jobId ? <Loader2 className="animate-spin" size={24} /> : <Play size={24} />}
                {jobId ? "Processing Multi-Swap..." : "Start Multi-Swap"}
              </button>
            </div>
          </div>"""

code = code.replace(ui_insert, ui_replacement)

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)
print("Patched FaceMappingStudio.tsx for export profiles and restoration")
