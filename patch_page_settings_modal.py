import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

old_modal = """                <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Cloud Cost Management</h3>
                
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
                </div>"""

new_modal = """                <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Hardware Configuration</h3>
                
                <div className="flex items-start gap-4 p-4 rounded-xl border border-slate-200 bg-white">
                  <div className="mt-0.5">
                    <Layers className={useCuda ? "text-indigo-600" : "text-slate-400"} size={20} />
                  </div>
                  <div className="flex-1">
                    <label className="flex items-center justify-between cursor-pointer">
                      <span className="font-medium text-slate-800 flex items-center gap-2">
                        CUDA Execution Mode
                        {gpuActive ? (
                          <span className="text-[10px] font-bold tracking-wide text-green-700 bg-green-100 px-1.5 py-0.5 rounded uppercase">Hardware Found</span>
                        ) : (
                          <span className="text-[10px] font-bold tracking-wide text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded uppercase">No GPU Found</span>
                        )}
                      </span>
                      <div className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${useCuda ? 'bg-indigo-600' : 'bg-slate-200'}`}>
                        <input type="checkbox" className="sr-only" checked={useCuda} onChange={(e) => setUseCuda(e.target.checked)} />
                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${useCuda ? 'translate-x-6' : 'translate-x-1'}`} />
                      </div>
                    </label>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                      Enable NVIDIA hardware acceleration for face detection and ONNX inference. Requires a compatible CUDA-enabled GPU and CUDA drivers installed on the host container.
                    </p>
                  </div>
                </div>

                <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider pt-2">Cloud Cost Management</h3>
                
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
                </div>"""

content = content.replace(old_modal, new_modal)

with open('app/page.tsx', 'w') as f:
    f.write(content)
