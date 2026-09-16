import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# Add saturation state
state_updates = """  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);
  const [saturation, setSaturation] = useState(100);
  const [showFilters, setShowFilters] = useState(false);"""

content = re.sub(r'(const \[brightness.*?setShowFilters\] = useState\(false\);\n)', state_updates + r'\n', content, flags=re.DOTALL)

# Update filter string
content = content.replace('filter: `brightness(${brightness}%) contrast(${contrast}%)`', 'filter: `brightness(${brightness}%) contrast(${contrast}%) saturate(${saturation}%)`')

# Update button styling to include saturation
content = content.replace('showFilters || brightness !== 100 || contrast !== 100', 'showFilters || brightness !== 100 || contrast !== 100 || saturation !== 100')

# Replace the whole filter popover content
old_popover = """              <div className="absolute bottom-full right-0 mb-2 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl p-4 shadow-2xl w-64 z-50">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="text-white text-sm font-semibold">Visual Inspection</h4>
                  <button onClick={() => { setBrightness(100); setContrast(100); }} className="text-xs text-white/50 hover:text-white transition-colors">Reset</button>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-xs text-white/70 mb-1.5">
                      <span>Brightness</span>
                      <span>{brightness}%</span>
                    </div>
                    <input 
                      type="range" 
                      min="0" 
                      max="200" 
                      value={brightness} 
                      onChange={(e) => setBrightness(Number(e.target.value))}
                      className="w-full h-1.5 bg-white/20 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-xs text-white/70 mb-1.5">
                      <span>Contrast</span>
                      <span>{contrast}%</span>
                    </div>
                    <input 
                      type="range" 
                      min="0" 
                      max="200" 
                      value={contrast} 
                      onChange={(e) => setContrast(Number(e.target.value))}
                      className="w-full h-1.5 bg-white/20 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                </div>
              </div>"""

new_popover = """              <div className="absolute bottom-full right-0 mb-2 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl p-4 shadow-2xl w-72 z-50">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-white text-sm font-semibold">Visual Inspection</h4>
                  <button onClick={() => { setBrightness(100); setContrast(100); setSaturation(100); }} className="text-xs text-white/50 hover:text-white transition-colors">Reset</button>
                </div>
                
                {/* Presets */}
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
                </div>

                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-xs text-white/70 mb-1.5">
                      <span>Brightness</span>
                      <span>{brightness}%</span>
                    </div>
                    <input 
                      type="range" 
                      min="0" 
                      max="200" 
                      value={brightness} 
                      onChange={(e) => setBrightness(Number(e.target.value))}
                      className="w-full h-1.5 bg-white/20 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-xs text-white/70 mb-1.5">
                      <span>Contrast</span>
                      <span>{contrast}%</span>
                    </div>
                    <input 
                      type="range" 
                      min="0" 
                      max="200" 
                      value={contrast} 
                      onChange={(e) => setContrast(Number(e.target.value))}
                      className="w-full h-1.5 bg-white/20 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-xs text-white/70 mb-1.5">
                      <span>Saturation</span>
                      <span>{saturation}%</span>
                    </div>
                    <input 
                      type="range" 
                      min="0" 
                      max="200" 
                      value={saturation} 
                      onChange={(e) => setSaturation(Number(e.target.value))}
                      className="w-full h-1.5 bg-white/20 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                </div>
              </div>"""

content = content.replace(old_popover, new_popover)

with open('app/page.tsx', 'w') as f:
    f.write(content)
