import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# 1. Imports
content = re.sub(r'(import \{[^\}]*?)( \} from \'lucide-react\';)', r'\1, Save, Plus\2', content)

# 2. State
state_updates = """  const [showBookmarksPanel, setShowBookmarksPanel] = useState(false);

  const [customPresets, setCustomPresets] = useState<{name: string, brightness: number, contrast: number, saturation: number, isSplitScreen: boolean}[]>([]);
  const [showPresetInput, setShowPresetInput] = useState(false);
  const [newPresetName, setNewPresetName] = useState('');
  
  const handleSavePreset = () => {
    if (!newPresetName.trim()) return;
    setCustomPresets([...customPresets, {
      name: newPresetName.trim(),
      brightness,
      contrast,
      saturation,
      isSplitScreen
    }]);
    setNewPresetName('');
    setShowPresetInput(false);
  };"""

content = content.replace("  const [showBookmarksPanel, setShowBookmarksPanel] = useState(false);", state_updates)

# 3. UI
ui_old = """                {/* Presets */}
                <div className="flex flex-wrap gap-1.5 mb-4">
                  <button 
                    onClick={() => { setBrightness(100); setContrast(150); setSaturation(100); }}
                    className="px-2 py-1 bg-white/10 hover:bg-white/20 text-white text-[10px] font-medium rounded transition-colors"
                  >
                    High Contrast
                  </button>
                  <button 
                    onClick={() => { setBrightness(150); setContrast(100); setSaturation(100); }}
                    className="px-2 py-1 bg-white/10 hover:bg-white/20 text-white text-[10px] font-medium rounded transition-colors"
                  >
                    High Brightness
                  </button>
                  <button 
                    onClick={() => { setBrightness(100); setContrast(100); setSaturation(0); }}
                    className="px-2 py-1 bg-white/10 hover:bg-white/20 text-white text-[10px] font-medium rounded transition-colors"
                  >
                    Desaturated
                  </button>
                </div>"""

ui_new = """                {/* Presets */}
                <div className="flex flex-col gap-2 mb-4">
                  <div className="flex flex-wrap gap-1.5">
                    <button 
                      onClick={() => { setBrightness(100); setContrast(150); setSaturation(100); }}
                      className="px-2 py-1 bg-white/10 hover:bg-white/20 text-white text-[10px] font-medium rounded transition-colors"
                    >
                      High Contrast
                    </button>
                    <button 
                      onClick={() => { setBrightness(150); setContrast(100); setSaturation(100); }}
                      className="px-2 py-1 bg-white/10 hover:bg-white/20 text-white text-[10px] font-medium rounded transition-colors"
                    >
                      High Brightness
                    </button>
                    <button 
                      onClick={() => { setBrightness(100); setContrast(100); setSaturation(0); }}
                      className="px-2 py-1 bg-white/10 hover:bg-white/20 text-white text-[10px] font-medium rounded transition-colors"
                    >
                      Desaturated
                    </button>
                  </div>
                  
                  {/* Custom Presets */}
                  <div className="border-t border-white/10 pt-2 mt-1">
                    <div className="flex justify-between items-center mb-1.5">
                      <span className="text-[10px] text-white/50 uppercase tracking-wider font-semibold">Custom Presets</span>
                      <button 
                        onClick={() => setShowPresetInput(!showPresetInput)}
                        className="text-white/50 hover:text-white flex items-center gap-1 text-[10px]"
                        title="Save Current View"
                      >
                        <Plus size={10} /> Save Current
                      </button>
                    </div>
                    
                    {showPresetInput && (
                      <div className="flex gap-1.5 mb-2">
                        <input 
                          type="text"
                          value={newPresetName}
                          onChange={(e) => setNewPresetName(e.target.value)}
                          placeholder="Preset name..."
                          className="flex-1 bg-black/50 border border-white/10 rounded px-2 py-1 text-[10px] text-white focus:outline-none focus:border-indigo-500"
                          autoFocus
                          onKeyDown={(e) => e.key === 'Enter' && handleSavePreset()}
                        />
                        <button 
                          onClick={handleSavePreset}
                          disabled={!newPresetName.trim()}
                          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-2 py-1 rounded flex items-center justify-center transition-colors"
                        >
                          <Save size={12} />
                        </button>
                      </div>
                    )}
                    
                    {customPresets.length > 0 && (
                      <div className="flex flex-wrap gap-1.5">
                        {customPresets.map((preset, idx) => (
                          <div key={idx} className="group relative">
                            <button 
                              onClick={() => {
                                setBrightness(preset.brightness);
                                setContrast(preset.contrast);
                                setSaturation(preset.saturation);
                                setIsSplitScreen(preset.isSplitScreen);
                              }}
                              className="px-2 py-1 bg-indigo-500/20 hover:bg-indigo-500/40 border border-indigo-500/30 text-indigo-200 text-[10px] font-medium rounded transition-colors pr-6"
                            >
                              {preset.name}
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setCustomPresets(customPresets.filter((_, i) => i !== idx));
                              }}
                              className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 text-indigo-300 hover:text-red-400 transition-all"
                            >
                              <X size={10} />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>"""

content = content.replace(ui_old, ui_new)

with open('app/page.tsx', 'w') as f:
    f.write(content)

