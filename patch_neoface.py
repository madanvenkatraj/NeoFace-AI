import sys

with open("components/NeoFaceStudio.tsx", "r") as f:
    code = f.read()

ui_insert = """              <div className="flex flex-col gap-3">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Resolution</label>"""

ui_replacement = """              <div className="flex flex-col gap-3">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Quality Mode</label>
                <div className="grid grid-cols-2 gap-2">
                  {[ { id: 'fast', label: '⚡ Fast' }, { id: 'hd', label: '✨ High Quality (HD)' } ].map(mode => (
                    <button 
                      key={mode.id}
                      onClick={() => setSetting('qualityMode', mode.id as any)}
                      className={`px-3 py-2 rounded-lg border text-sm font-semibold transition-all ${
                        (present.qualityMode || 'hd') === mode.id ? 'bg-violet-500/20 border-violet-500/50 text-violet-300' : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                      }`}
                    >
                      {mode.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex flex-col gap-3">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Resolution</label>"""

code = code.replace(ui_insert, ui_replacement)

with open("components/NeoFaceStudio.tsx", "w") as f:
    f.write(code)
print("patched NeoFaceStudio.tsx")
