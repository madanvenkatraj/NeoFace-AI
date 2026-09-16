import re

with open('components/NeoFaceStudio.tsx', 'r') as f:
    content = f.read()

# 1. Icons
if "Flame," not in content:
    content = content.replace("  Zap\n}", "  Zap,\n  Flame,\n  Trash2\n}")

# 2. States & Cross-tab sync
new_states = """  // Batch Queue
  const [showBatchQueue, setShowBatchQueue] = useState(false);
  const [smartPrioritization, setSmartPrioritization] = useState(false);
  const [showMaskOverlay, setShowMaskOverlay] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(false);

  // Tab Sync (Processing History)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'neoface_batch_jobs' && e.newValue) {
        try {
          setBatchJobsEx(JSON.parse(e.newValue));
        } catch(err) {}
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  useEffect(() => {
    localStorage.setItem('neoface_batch_jobs', JSON.stringify(batchJobsEx));
  }, [batchJobsEx]);
"""
content = content.replace("  // Batch Queue\n  const [showBatchQueue, setShowBatchQueue] = useState(false);", new_states)

# 3. Modify savedSources initial state
old_sources = """  const [savedSources, setSavedSources] = useState([
    {id: 's1', url: 'https://picsum.photos/seed/source1/200/200', label: 'Source A', gender: 'Female'},
    {id: 's2', url: 'https://picsum.photos/seed/source2/200/200', label: 'Saved B', gender: 'Male'},
    {id: 's3', url: 'https://picsum.photos/seed/source3/200/200', label: 'Saved C', gender: 'Female'}
  ]);"""

new_sources = """  const [savedSources, setSavedSources] = useState([
    {id: 's1', url: 'https://picsum.photos/seed/source1/200/200', label: 'Source A', gender: 'Female', confidence: 0.98},
    {id: 's2', url: 'https://picsum.photos/seed/source2/200/200', label: 'Saved B', gender: 'Male', confidence: 0.95},
    {id: 's3', url: 'https://picsum.photos/seed/source4/200/200', label: 'Low Qual C', gender: 'Female', confidence: 0.65},
    {id: 's4', url: 'https://picsum.photos/seed/source4/200/200', label: 'Duplicate C', gender: 'Female', confidence: 0.92}
  ]);"""
if old_sources in content:
    content = content.replace(old_sources, new_sources)

# 4. Smart Prioritization in Batch Queue Modal
old_batch_header = """              <div className="p-5 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
                <h2 className="text-lg font-bold text-white flex items-center gap-2"><ListOrdered size={18} className="text-emerald-400" /> Batch Queue</h2>
                <button onClick={() => setShowBatchQueue(false)} className="text-slate-400 hover:text-white transition-colors"><X size={20} /></button>
              </div>"""
new_batch_header = """              <div className="p-5 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
                <h2 className="text-lg font-bold text-white flex items-center gap-2"><ListOrdered size={18} className="text-emerald-400" /> Batch Queue</h2>
                <button onClick={() => setShowBatchQueue(false)} className="text-slate-400 hover:text-white transition-colors"><X size={20} /></button>
              </div>
              <div className="px-5 py-3 border-b border-white/5 bg-black/40 flex justify-between items-center shadow-inner">
                <div className="flex flex-col">
                  <span className="text-xs font-semibold text-slate-300">Smart Prioritization</span>
                  <span className="text-[9px] text-slate-500">Auto-sequence by resolution & complexity</span>
                </div>
                <button 
                  onClick={() => {
                    const nextVal = !smartPrioritization;
                    setSmartPrioritization(nextVal);
                    if (nextVal) {
                       const sorted = [...batchJobsEx].sort((a, b) => b.name.localeCompare(a.name));
                       setBatchJobsEx(sorted);
                    } else {
                       const original = [...batchJobsEx].sort((a, b) => a.name.localeCompare(b.name));
                       setBatchJobsEx(original);
                    }
                  }}
                  className={`w-9 h-5 rounded-full flex items-center transition-colors p-0.5 ${smartPrioritization ? 'bg-cyan-500' : 'bg-slate-700'}`}
                >
                  <div className={`w-4 h-4 rounded-full bg-white transition-transform ${smartPrioritization ? 'translate-x-4' : 'translate-x-0'} shadow-sm`} />
                </button>
              </div>"""
content = content.replace(old_batch_header, new_batch_header)

# 5. Mask Overlay Toggle
old_mask_desc = """              <p className="text-xs text-slate-400">
                Paint over areas you want to strictly blend or exclude (e.g., hair, glasses, hands). 
                The mask indicates regions that will be seamlessly passed to the GFPGAN/CodeFormer upscaler.
              </p>"""
new_mask_desc = """              <div className="flex justify-between items-start">
                <p className="text-xs text-slate-400 max-w-[70%]">
                  Paint over areas you want to strictly blend or exclude (e.g., hair, glasses, hands). 
                  The mask indicates regions that will be seamlessly passed to the GFPGAN/CodeFormer upscaler.
                </p>
                <label className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-slate-300 cursor-pointer bg-white/5 px-2 py-1.5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors">
                  <input type="checkbox" className="form-checkbox rounded bg-slate-800 border-white/20 text-fuchsia-500 focus:ring-fuchsia-500 focus:ring-offset-slate-900" checked={showMaskOverlay} onChange={() => setShowMaskOverlay(!showMaskOverlay)} />
                  Overlay Focus
                </label>
              </div>"""
content = content.replace(old_mask_desc, new_mask_desc)

old_mask_pts = """                {maskPoints.map((pt, i) => (
                  <div key={i} className="absolute w-8 h-8 bg-emerald-500/40 rounded-full blur-[2px] pointer-events-none" style={{ left: `${pt.x}%`, top: `${pt.y}%`, transform: 'translate(-50%, -50%)' }} />
                ))}"""
new_mask_pts = """                {showMaskOverlay ? maskPoints.map((pt, i) => (
                  <div key={i} className="absolute w-8 h-8 bg-fuchsia-500/70 mix-blend-screen rounded-full blur-[2px] pointer-events-none" style={{ left: `${pt.x}%`, top: `${pt.y}%`, transform: 'translate(-50%, -50%)', boxShadow: '0 0 10px rgba(217, 70, 239, 0.5)' }} />
                )) : maskPoints.map((pt, i) => (
                  <div key={i} className="absolute w-8 h-8 bg-emerald-500/40 rounded-full blur-[2px] pointer-events-none" style={{ left: `${pt.x}%`, top: `${pt.y}%`, transform: 'translate(-50%, -50%)' }} />
                ))}"""
content = content.replace(old_mask_pts, new_mask_pts)


# 6. Automated Cleanup Routine (Source Face Gallery)
old_gallery_filter = """              <div className="flex items-center justify-between">
                <p className="text-xs text-slate-400">Select a saved face to map to the target, or upload a new one.</p>
                <div className="flex items-center gap-1 bg-black/50 p-1 rounded-lg border border-white/10">"""
new_gallery_filter = """              <div className="flex items-center justify-between">
                <p className="text-xs text-slate-400">Select a saved face to map to the target, or upload a new one.</p>
                <div className="flex gap-3">
                  <button 
                    onClick={() => {
                      // Filter duplicates and low-confidence
                      const seen = new Set();
                      const cleaned = savedSources.filter(s => {
                        const isDup = seen.has(s.url);
                        seen.add(s.url);
                        return !isDup && (s.confidence === undefined || s.confidence >= 0.8);
                      });
                      setSavedSources(cleaned);
                    }}
                    className="flex items-center gap-1.5 px-3 py-1 bg-rose-500/10 border border-rose-500/20 rounded-lg text-[10px] font-bold text-rose-400 hover:bg-rose-500/20 hover:text-rose-300 transition-colors uppercase tracking-widest"
                    title="Remove blurry or duplicate faces"
                  >
                    <Trash2 size={12} /> Clean Library
                  </button>
                  <div className="flex items-center gap-1 bg-black/50 p-1 rounded-lg border border-white/10">"""
content = content.replace(old_gallery_filter, new_gallery_filter)

old_source_image = """                    <div className="relative w-full aspect-square rounded-xl overflow-hidden border-2 border-white/10 group-hover:border-cyan-400 transition-colors">
                      <Image src={source.url} alt={source.label} fill className="object-cover" referrerPolicy="no-referrer" />
                    </div>"""
new_source_image = """                    <div className="relative w-full aspect-square rounded-xl overflow-hidden border-2 border-white/10 group-hover:border-cyan-400 transition-colors">
                      <Image src={source.url} alt={source.label} fill className={`object-cover ${source.confidence && source.confidence < 0.8 ? 'blur-[1px] opacity-40 grayscale mix-blend-luminosity' : ''}`} referrerPolicy="no-referrer" />
                      {source.confidence && source.confidence < 0.8 && (
                        <div className="absolute inset-0 bg-red-900/10 flex flex-col items-center justify-center pointer-events-none">
                          <span className="bg-rose-600/90 text-white text-[8px] font-bold px-1.5 py-0.5 rounded shadow whitespace-nowrap">LOW QUAL</span>
                        </div>
                      )}
                      {source.confidence && source.confidence >= 0.8 && (
                        <div className="absolute bottom-1 right-1 bg-black/70 backdrop-blur-sm text-emerald-400 text-[8px] font-bold px-1.5 py-0.5 rounded shadow">
                          {Math.round(source.confidence * 100)}% Match
                        </div>
                      )}
                    </div>"""
content = content.replace(old_source_image, new_source_image)

# 7. Micro-Expression Heatmap Visualization
old_exp_btn = """                        <button 
                          onClick={() => setMicroExpressions(!microExpressions)}
                          className={`flex-1 sm:flex-none px-3 py-1.5 rounded border text-[10px] font-bold uppercase tracking-wider flex items-center justify-center gap-1.5 transition-colors ${microExpressions ? 'bg-violet-500/20 text-violet-400 border-violet-500/30' : 'bg-black/50 text-slate-400 border-white/10'}`}
                          title="Isolate and map target micro-expressions onto source"
                        >
                          <BrainCircuit size={12} /> Expressions {microExpressions ? 'ON' : 'OFF'}
                        </button>
                      </div>"""
new_exp_btn = """                        <button 
                          onClick={() => setMicroExpressions(!microExpressions)}
                          className={`flex-1 sm:flex-none px-3 py-1.5 rounded border text-[10px] font-bold uppercase tracking-wider flex items-center justify-center gap-1.5 transition-colors ${microExpressions ? 'bg-violet-500/20 text-violet-400 border-violet-500/30' : 'bg-black/50 text-slate-400 border-white/10'}`}
                          title="Isolate and map target micro-expressions onto source"
                        >
                          <BrainCircuit size={12} /> Expressions {microExpressions ? 'ON' : 'OFF'}
                        </button>
                        {microExpressions && (
                           <button 
                             onClick={() => setShowHeatmap(!showHeatmap)}
                             className={`flex-1 sm:flex-none px-3 py-1.5 rounded border text-[10px] font-bold uppercase tracking-wider flex items-center justify-center gap-1.5 transition-colors ${showHeatmap ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' : 'bg-black/50 text-slate-400 border-white/10'}`}
                             title="Visualize Facial Movement Intensity"
                           >
                             <Flame size={12} /> Heatmap {showHeatmap ? 'ON' : 'OFF'}
                           </button>
                        )}
                      </div>"""
content = content.replace(old_exp_btn, new_exp_btn)

old_source_assignment = """                              <Image 
                                src={savedSources.find(s => s.id === mappedFaces[target.id])?.url || MOCK_SOURCE_FACES[0].url} 
                                alt="Source face" fill referrerPolicy="no-referrer" className="rounded-full border-2 border-emerald-500/50 object-cover" 
                              />"""
new_source_assignment = """                              <Image 
                                src={savedSources.find(s => s.id === mappedFaces[target.id])?.url || MOCK_SOURCE_FACES[0].url} 
                                alt="Source face" fill referrerPolicy="no-referrer" className="rounded-full border-2 border-emerald-500/50 object-cover" 
                              />
                              {showHeatmap && microExpressions && (
                                <div 
                                  className="absolute inset-0 rounded-full mix-blend-screen opacity-80 pointer-events-none" 
                                  style={{ background: 'radial-gradient(circle at 50% 60%, rgba(250,204,21,0.7) 0%, rgba(239,68,68,0.5) 40%, rgba(0,0,0,0.8) 80%)' }} 
                                />
                              )}
                              {showHeatmap && microExpressions && (
                                <div className="absolute inset-x-0 bottom-[-16px] flex justify-center pointer-events-none">
                                  <span className="text-[7px] bg-amber-900/90 text-amber-300 px-1 py-0.5 rounded shadow whitespace-nowrap uppercase tracking-widest border border-amber-500/50">Intensity Map</span>
                                </div>
                              )}"""
content = content.replace(old_source_assignment, new_source_assignment)

with open('components/NeoFaceStudio.tsx', 'w') as f:
    f.write(content)

