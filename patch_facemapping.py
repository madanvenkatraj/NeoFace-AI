import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

code = code.replace(
    "const [jobId, setJobId] = useState<string | null>(null);",
    "const [jobId, setJobId] = useState<string | null>(null);\n  const [qualityMode, setQualityMode] = useState<'hd' | 'fast'>('hd');"
)

code = code.replace(
    "formData.append('is_video', isVideo.toString());",
    "formData.append('is_video', isVideo.toString());\n      formData.append('quality_mode', qualityMode);"
)

ui_insert = """            <div className="text-sm font-medium text-slate-600">
              <span className="text-indigo-600 font-bold">{Object.keys(faceMappings).length}</span> of {detectedFaces.length} faces mapped
            </div>"""

ui_replacement = """            <div className="flex flex-col md:flex-row items-center gap-6">
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
            </div>"""

code = code.replace(ui_insert, ui_replacement)

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)
print("patched FaceMappingStudio.tsx")
