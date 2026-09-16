import sys

with open("components/NeoFaceStudio.tsx", "r") as f:
    code = f.read()

import_insert = "import AuthButton from './AuthButton';"
import_replacement = "import AuthButton from './AuthButton';\nimport SwapHistoryModal from './SwapHistoryModal';\nimport { History } from 'lucide-react';"

code = code.replace(import_insert, import_replacement)

state_insert = "  const [showExportSettings, setShowExportSettings] = useState(false);"
state_replacement = "  const [showExportSettings, setShowExportSettings] = useState(false);\n  const [showHistory, setShowHistory] = useState(false);"

code = code.replace(state_insert, state_replacement)

header_insert = """          <div className="flex items-center gap-2">
            <CloudSyncButton />
            <AuthButton />
          </div>"""

header_replacement = """          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowHistory(true)}
              className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg text-sm font-semibold transition-colors flex items-center gap-2 border border-white/10"
            >
              <History size={16} className="text-indigo-400" />
              History
            </button>
            <CloudSyncButton />
            <AuthButton />
          </div>"""

code = code.replace(header_insert, header_replacement)

modal_insert = """      {/* Export Settings Modal */}"""

modal_replacement = """      <SwapHistoryModal isOpen={showHistory} onClose={() => setShowHistory(false)} />

      {/* Export Settings Modal */}"""

code = code.replace(modal_insert, modal_replacement)

with open("components/NeoFaceStudio.tsx", "w") as f:
    f.write(code)
print("patched NeoFaceStudio.tsx")
