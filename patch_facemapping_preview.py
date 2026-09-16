import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

# Add import
import_insert = "import ProcessingOverlay from './ProcessingOverlay';"
import_replacement = "import ProcessingOverlay from './ProcessingOverlay';\nimport BeforeAfterPreview from './BeforeAfterPreview';"

code = code.replace(import_insert, import_replacement)

# Replace the result block
ui_insert = """          {resultPath && (
            <div className="flex flex-col gap-4 mt-8 animate-in slide-in-from-bottom-4">
              <div className="p-6 bg-emerald-50 border border-emerald-200 rounded-2xl flex flex-col md:flex-row justify-between items-center gap-4">
                <div className="flex flex-col gap-2">
                  <div className="flex items-center gap-3 text-emerald-700 font-semibold text-lg">
                    <CheckCircle2 size={28} /> Multi-Swap Completed
                  </div>
                </div>
                <a 
                  href={`${API_URL}/outputs/${resultPath.split('/').pop()}`}
                  download={`neoface_multiswap.${resultPath.split('.').pop()}`}
                  className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold shadow-sm transition-all whitespace-nowrap"
                >
                  Download Result
                </a>
              </div>
              
              {jobMetrics && (
                <ProcessingDiagnostics metrics={jobMetrics} />
              )}
            </div>
          )}"""

ui_replacement = """          {resultPath && targetPreviewUrl && (
            <div className="flex flex-col gap-4 mt-8 animate-in slide-in-from-bottom-4">
              <div className="flex items-center gap-3 text-emerald-700 font-semibold text-lg mb-2">
                <CheckCircle2 size={28} /> Multi-Swap Completed
              </div>
              
              <BeforeAfterPreview 
                originalSrc={targetPreviewUrl}
                resultSrc={resultPath.startsWith('http') ? resultPath : `${API_URL}/outputs/${resultPath.split('/').pop()}`}
                isVideo={isVideo}
                downloadName={`neoface_multiswap.${resultPath.split('.').pop()}`}
              />
              
              {jobMetrics && (
                <div className="mt-4">
                  <ProcessingDiagnostics metrics={jobMetrics} />
                </div>
              )}
            </div>
          )}"""

code = code.replace(ui_insert, ui_replacement)

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)
print("patched FaceMappingStudio.tsx")
