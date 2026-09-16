import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

import_insert = "import ProgressBar from './ProgressBar';"
import_replacement = "import ProgressBar from './ProgressBar';\nimport ProcessingOverlay from './ProcessingOverlay';"

code = code.replace(import_insert, import_replacement)

ui_insert = """          {jobId && (
            <div className="w-full mt-6 bg-slate-50 p-6 rounded-2xl border border-slate-200">
              <ProgressBar 
                progress={progress} 
                statusMsg={statusMsg || "Initializing pipeline..."} 
                theme="indigo" 
              />
            </div>
          )}"""

ui_replacement = """          <ProcessingOverlay
            isVisible={!!jobId}
            progress={progress}
            statusMsg={statusMsg || "Initializing pipeline..."}
            theme="indigo"
          />"""

code = code.replace(ui_insert, ui_replacement)

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)
print("patched FaceMappingStudio.tsx")
