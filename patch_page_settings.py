import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# 1. Add state
state_block = """  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [autoSpindown, setAutoSpindown] = useState(false);
  
  useEffect(() => {
    if (typeof window !== 'undefined') {
      setAutoSpindown(localStorage.getItem('neoFace_autoSpindown') === 'true');
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('neoFace_autoSpindown', autoSpindown.toString());
    
    if (!autoSpindown) return;
    
    const checkIdle = async () => {
      try {
        const res = await fetch(`${API_URL}/api/system/idle`);
        if (res.ok) {
          const data = await res.json();
          if (data.is_idle && data.idle_minutes > 15) {
             if (typeof Notification !== 'undefined') {
                 if (Notification.permission === 'granted') {
                    new Notification('NeoFace AI - GPU Worker Idle', {
                      body: `Worker has been idle for ${Math.round(data.idle_minutes)} minutes. Consider spinning down to save costs.`,
                    });
                 } else if (Notification.permission !== 'denied') {
                    Notification.requestPermission();
                 }
             }
          }
        }
      } catch (err) {}
    };
    
    const interval = setInterval(checkIdle, 60000);
    checkIdle();
    return () => clearInterval(interval);
  }, [autoSpindown]);
"""

content = content.replace("  const [isSidebarOpen, setIsSidebarOpen] = useState(false);", state_block)


# 2. Add Settings Button to header
header_btn_old = """          <button 
            onClick={() => {
              setIsSidebarOpen(true);
              fetchHistory();
            }}
            className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-indigo-600 transition-colors shadow-sm"
          >
            <History size={18} />
            View History
          </button>"""

header_btn_new = """          <div className="flex items-center gap-3">
            <button 
              onClick={() => setIsSettingsOpen(true)}
              className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-sm"
            >
              <Settings size={18} />
              Settings
            </button>
            <button 
              onClick={() => {
                setIsSidebarOpen(true);
                fetchHistory();
              }}
              className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-indigo-600 transition-colors shadow-sm"
            >
              <History size={18} />
              View History
            </button>
          </div>"""

content = content.replace(header_btn_old, header_btn_new)

# 3. Add Settings Modal
settings_modal = """
      {/* Settings Modal */}
      {isSettingsOpen && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setIsSettingsOpen(false)}>
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden" onClick={e => e.stopPropagation()}>
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50">
              <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <Settings className="text-slate-500" size={24} /> Settings
              </h2>
              <button onClick={() => setIsSettingsOpen(false)} className="text-slate-400 hover:text-slate-600 p-2 rounded-full hover:bg-slate-200 transition-colors">
                <X size={20} />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Cloud Cost Management</h3>
                
                <div className="flex items-start gap-4 p-4 rounded-xl border border-slate-200 bg-white">
                  <div className="mt-0.5">
                    <Bell className={autoSpindown ? "text-indigo-600" : "text-slate-400"} size={20} />
                  </div>
                  <div className="flex-1">
                    <label className="flex items-center justify-between cursor-pointer">
                      <span className="font-medium text-slate-800">Idle GPU Notifications</span>
                      <div className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${autoSpindown ? 'bg-indigo-600' : 'bg-slate-200'}`}>
                        <input type="checkbox" className="sr-only" checked={autoSpindown} onChange={(e) => {
                          setAutoSpindown(e.target.checked);
                          if (e.target.checked && typeof Notification !== 'undefined' && Notification.permission !== 'granted') {
                            Notification.requestPermission();
                          }
                        }} />
                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${autoSpindown ? 'translate-x-6' : 'translate-x-1'}`} />
                      </div>
                    </label>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                      Automatically notify me when the GPU worker has been idle for more than 15 minutes to prevent unnecessary cloud costs.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end">
              <button onClick={() => setIsSettingsOpen(false)} className="px-5 py-2.5 bg-slate-900 text-white font-medium rounded-xl hover:bg-slate-800 transition-colors">
                Done
              </button>
            </div>
          </div>
        </div>
      )}
"""

# Insert modal before `return (` ? Wait, `return (` is at the beginning.
# Better to insert it right before the closing `</main>`.
content = content.replace("</main>", settings_modal + "\n    </main>")

with open('app/page.tsx', 'w') as f:
    f.write(content)
