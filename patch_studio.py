import os
import re

def patch():
    with open('components/NeoFaceStudio.tsx', 'r') as f:
        content = f.read()

    # 1. Imports
    if 'Save' not in content:
        content = content.replace("  SlidersHorizontal\n}", "  SlidersHorizontal,\n  Save,\n  Keyboard,\n  Focus,\n  FolderHeart,\n  MonitorPlay\n}")

    # 2. States
    state_code = """  // Masking Tool
  const [isMasking, setIsMasking] = useState(false);
  const [isDrawing, setIsDrawing] = useState(false);
  const [maskPoints, setMaskPoints] = useState<{x: number, y: number}[]>([]);

  // New Features
  const [showExportSettings, setShowExportSettings] = useState(false);
  const [exportPreset, setExportPreset] = useState('1080p60');
  const [showLandmarks, setShowLandmarks] = useState(false);
  const [showGallery, setShowGallery] = useState(false);
  const [activeTargetForGallery, setActiveTargetForGallery] = useState<string | null>(null);
  const [savedSources, setSavedSources] = useState([...MOCK_SOURCE_FACES, {id: 's2', url: 'https://picsum.photos/seed/source2/200/200', label: 'Saved B'}]);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [isPlaying, setIsPlaying] = useState(true);

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.code === 'Space' && currentStep === 5) {
        e.preventDefault();
        setIsPlaying(p => !p);
      }
      if ((e.ctrlKey || e.metaKey) && e.code === 'Enter' && currentStep === 3) {
        e.preventDefault();
        if (Object.keys(mappedFaces).length === MOCK_TARGET_FACES.length) {
          handleStartProcessing();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentStep, mappedFaces]);
"""
    if 'showExportSettings' not in content:
        content = re.sub(r'// Masking Tool.*?const \[maskPoints.*?\];\n', state_code, content, flags=re.DOTALL)

    # 3. Add Shortcuts to Header
    old_header = """          <div className="flex items-center gap-2">
            <button 
              onClick={() => setShowBatchQueue(true)}"""
    new_header = """          <div className="flex items-center gap-2">
            <button 
              onClick={() => setShowShortcuts(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 text-xs font-semibold transition-colors border border-white/10"
            >
              <Keyboard size={14} /> Shortcuts
            </button>
            <button 
              onClick={() => setShowBatchQueue(true)}"""
    content = content.replace(old_header, new_header)

    # 4. Landmarks in targetPreview
    old_target_preview = """                  <div className="relative aspect-video bg-black/50 overflow-hidden flex items-center justify-center">
                    {targetPreview ? (
                      <Image src={targetPreview} alt="Preview" fill referrerPolicy="no-referrer" className="object-cover opacity-70" />
                    ) : (
                      <Video size={48} className="text-white/10" />
                    )}
                  </div>"""
    new_target_preview = """                  <div className="relative aspect-video bg-black/50 overflow-hidden flex items-center justify-center">
                    {targetPreview ? (
                      <>
                        <Image src={targetPreview} alt="Preview" fill referrerPolicy="no-referrer" className="object-cover opacity-70" />
                        {showLandmarks && (
                          <div className="absolute inset-0 pointer-events-none">
                            {/* Simulated Landmark Dots */}
                            <div className="absolute top-[35%] left-[45%] w-1.5 h-1.5 bg-emerald-400 rounded-full shadow-[0_0_8px_#34d399]" />
                            <div className="absolute top-[35%] right-[45%] w-1.5 h-1.5 bg-emerald-400 rounded-full shadow-[0_0_8px_#34d399]" />
                            <div className="absolute top-[50%] left-[50%] -translate-x-1/2 w-1.5 h-1.5 bg-emerald-400 rounded-full shadow-[0_0_8px_#34d399]" />
                            <div className="absolute top-[65%] left-[48%] w-1.5 h-1.5 bg-emerald-400 rounded-full shadow-[0_0_8px_#34d399]" />
                            <div className="absolute top-[65%] right-[48%] w-1.5 h-1.5 bg-emerald-400 rounded-full shadow-[0_0_8px_#34d399]" />
                            
                            <div className="absolute top-4 left-4 bg-black/50 backdrop-blur border border-emerald-500/30 text-emerald-400 px-2 py-1 rounded text-[10px] font-bold uppercase flex items-center gap-1">
                              <Focus size={12} /> Alignment Active
                            </div>
                          </div>
                        )}
                      </>
                    ) : (
                      <Video size={48} className="text-white/10" />
                    )}
                  </div>"""
    content = content.replace(old_target_preview, new_target_preview)

    # 5. Landmarks toggle button in Detected Faces header
    old_detected_header = """                  <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                    <Camera size={16} className="text-violet-400" />
                    Detected Faces ({MOCK_TARGET_FACES.length})
                  </h3>"""
    new_detected_header = """                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                      <Camera size={16} className="text-violet-400" />
                      Detected Faces ({MOCK_TARGET_FACES.length})
                    </h3>
                    <button 
                      onClick={() => setShowLandmarks(!showLandmarks)}
                      className={`px-2 py-1 rounded border text-xs font-bold transition-colors flex items-center gap-1 ${
                        showLandmarks ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-white/5 text-slate-400 border-white/10 hover:text-white'
                      }`}
                    >
                      <Focus size={12} /> {showLandmarks ? 'Hide Landmarks' : 'Show Landmarks'}
                    </button>
                  </div>"""
    content = content.replace(old_detected_header, new_detected_header)

    # 6. Source Library Gallery in Step 3
    # Replace the "Assign" button
    old_assign_btn = """                          ) : (
                            <button 
                              onClick={() => setMappedFaces({...mappedFaces, [target.id]: 's1'})} // Mock selection
                              className="w-20 h-20 rounded-full border border-dashed border-white/30 bg-white/5 hover:bg-white/10 flex flex-col items-center justify-center text-slate-400 hover:text-white hover:border-cyan-400 transition-all group"
                            >
                              <UploadCloud size={18} className="mb-1 group-hover:scale-110 transition-transform" />
                              <span className="text-[9px] uppercase tracking-wider font-semibold">Assign</span>
                            </button>
                          )}"""
    new_assign_btn = """                          ) : (
                            <button 
                              onClick={() => { setActiveTargetForGallery(target.id); setShowGallery(true); }}
                              className="w-20 h-20 rounded-full border border-dashed border-white/30 bg-white/5 hover:bg-white/10 flex flex-col items-center justify-center text-slate-400 hover:text-white hover:border-cyan-400 transition-all group"
                            >
                              <FolderHeart size={18} className="mb-1 group-hover:scale-110 transition-transform" />
                              <span className="text-[9px] uppercase tracking-wider font-semibold">Library</span>
                            </button>
                          )}"""
    content = content.replace(old_assign_btn, new_assign_btn)
    
    # 7. Add brush tool to the selected source image
    old_source_img = """                          {mappedFaces[target.id] && mappedFaces[target.id] !== 'skip' ? (
                            <div className="relative group cursor-pointer w-20 h-20">
                              <Image src={MOCK_SOURCE_FACES[0].url} alt="Source face" fill referrerPolicy="no-referrer" className="rounded-full border-2 border-emerald-500/50 object-cover" />"""
    new_source_img = """                          {mappedFaces[target.id] && mappedFaces[target.id] !== 'skip' ? (
                            <div className="relative group cursor-pointer w-20 h-20">
                              {/* Resolve selected source url */}
                              <Image 
                                src={savedSources.find(s => s.id === mappedFaces[target.id])?.url || MOCK_SOURCE_FACES[0].url} 
                                alt="Source face" fill referrerPolicy="no-referrer" className="rounded-full border-2 border-emerald-500/50 object-cover" 
                              />
                              <button 
                                onClick={() => setIsMasking(true)} 
                                className="absolute bottom-0 right-0 p-1.5 bg-black/80 rounded-full backdrop-blur text-white opacity-0 group-hover:opacity-100 transition-opacity hover:text-emerald-400 z-10 border border-white/20 shadow-lg"
                                title="Paint Blend Mask"
                              >
                                <Brush size={12} />
                              </button>"""
    content = content.replace(old_source_img, new_source_img)

    # 8. Export Settings Modal Toggle
    old_export = """                  <button className="px-5 py-2 rounded-lg bg-white text-black hover:bg-slate-200 text-sm font-bold transition-colors flex items-center gap-2 shadow-[0_0_20px_rgba(255,255,255,0.2)]">
                    <Download size={16} /> Full Render
                  </button>"""
    new_export = """                  <button 
                    onClick={() => setShowExportSettings(true)}
                    className="px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 transition-colors border border-white/10"
                    title="Export Settings"
                  >
                    <Settings2 size={16} />
                  </button>
                  <button className="px-5 py-2 rounded-lg bg-white text-black hover:bg-slate-200 text-sm font-bold transition-colors flex items-center gap-2 shadow-[0_0_20px_rgba(255,255,255,0.2)]">
                    <Download size={16} /> Full Render
                  </button>"""
    content = content.replace(old_export, new_export)
    
    # 9. Modals (Gallery, Settings, Shortcuts)
    modals = """
      {/* Source Face Gallery Modal */}
      <AnimatePresence>
        {showGallery && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} className="bg-slate-900 border border-white/10 p-6 rounded-2xl w-full max-w-xl flex flex-col gap-4 shadow-2xl">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-white flex items-center gap-2"><FolderHeart className="text-cyan-400" /> Source Face Library</h3>
                <button onClick={() => setShowGallery(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
              </div>
              <p className="text-xs text-slate-400 mb-2">Select a saved face to map to the target, or upload a new one.</p>
              
              <div className="grid grid-cols-4 gap-4 mb-4">
                {savedSources.map(source => (
                  <button 
                    key={source.id} 
                    onClick={() => {
                      if(activeTargetForGallery) {
                        setMappedFaces(prev => ({...prev, [activeTargetForGallery]: source.id}));
                      }
                      setShowGallery(false);
                    }}
                    className="flex flex-col items-center gap-2 group"
                  >
                    <div className="relative w-full aspect-square rounded-xl overflow-hidden border-2 border-white/10 group-hover:border-cyan-400 transition-colors">
                      <Image src={source.url} alt={source.label} fill className="object-cover" referrerPolicy="no-referrer" />
                    </div>
                    <span className="text-xs font-semibold text-slate-300 group-hover:text-white truncate w-full text-center">{source.label}</span>
                  </button>
                ))}
                
                <button className="flex flex-col items-center justify-center gap-2 w-full aspect-square rounded-xl border-2 border-dashed border-white/20 bg-white/5 hover:bg-white/10 hover:border-cyan-400 transition-colors text-slate-400 hover:text-white">
                  <UploadCloud size={24} />
                  <span className="text-xs font-bold uppercase tracking-wider">New</span>
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Export Settings Modal */}
      <AnimatePresence>
        {showExportSettings && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} className="bg-slate-900 border border-white/10 p-6 rounded-2xl w-full max-w-sm flex flex-col gap-6 shadow-2xl">
              <div className="flex justify-between items-center border-b border-white/10 pb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2"><Settings2 className="text-violet-400" /> Export Settings</h3>
                <button onClick={() => setShowExportSettings(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
              </div>
              
              <div className="flex flex-col gap-3">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Saved Presets</label>
                <div className="grid grid-cols-1 gap-2">
                  {[
                    { id: '4k60', label: 'Cinematic High (4K, 60fps)' },
                    { id: '1080p60', label: 'Standard (1080p, 60fps)' },
                    { id: '720p30', label: 'Fast Draft (720p, 30fps)' }
                  ].map(preset => (
                    <button 
                      key={preset.id}
                      onClick={() => setExportPreset(preset.id)}
                      className={`px-4 py-3 rounded-lg border text-sm font-semibold flex justify-between items-center transition-all ${
                        exportPreset === preset.id ? 'bg-violet-500/20 border-violet-500/50 text-violet-300' : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                      }`}
                    >
                      {preset.label}
                      {exportPreset === preset.id && <CheckCircle2 size={16} className="text-violet-400" />}
                    </button>
                  ))}
                </div>
              </div>
              
              <div className="pt-2">
                <button onClick={() => setShowExportSettings(false)} className="w-full py-2.5 rounded-lg bg-white text-black font-bold text-sm hover:bg-slate-200 transition-colors">
                  Save Configuration
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Shortcuts Cheat Sheet */}
      <AnimatePresence>
        {showShortcuts && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" onClick={() => setShowShortcuts(false)}>
            <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 20, opacity: 0 }} className="bg-slate-900 border border-white/10 p-6 rounded-2xl w-full max-w-md flex flex-col gap-4 shadow-2xl" onClick={e => e.stopPropagation()}>
              <div className="flex justify-between items-center border-b border-white/10 pb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2"><Keyboard className="text-cyan-400" /> Keyboard Shortcuts</h3>
                <button onClick={() => setShowShortcuts(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
              </div>
              <div className="flex flex-col gap-3 py-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-300">Play/Pause Timeline</span>
                  <div className="flex gap-1"><kbd className="px-2 py-1 bg-white/10 rounded border border-white/20 text-xs font-mono text-white">Space</kbd></div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-300">Start Processing</span>
                  <div className="flex gap-1">
                    <kbd className="px-2 py-1 bg-white/10 rounded border border-white/20 text-xs font-mono text-white">Ctrl</kbd>
                    <span className="text-slate-500">+</span>
                    <kbd className="px-2 py-1 bg-white/10 rounded border border-white/20 text-xs font-mono text-white">Enter</kbd>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-300">Toggle Landmarks</span>
                  <div className="flex gap-1"><kbd className="px-2 py-1 bg-white/10 rounded border border-white/20 text-xs font-mono text-white">L</kbd></div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
"""
    content = content.replace("    </div>\n  );\n}", modals + "\n    </div>\n  );\n}")

    with open('components/NeoFaceStudio.tsx', 'w') as f:
        f.write(content)

patch()
