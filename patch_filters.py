import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# Add SlidersHorizontal to imports
if "SlidersHorizontal" not in content:
    content = re.sub(r'(import \{[^\}]*?)( \} from \'lucide-react\';)', r'\1, SlidersHorizontal\2', content)

# Add states
state_updates = """  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);
  const [showFilters, setShowFilters] = useState(false);
"""

content = re.sub(r'(const \[playbackRate, setPlaybackRate\] = useState<number>\(1\);\n)', r'\1' + state_updates, content)

# Add filter style to wrapper divs
before_transform_search = r'(<div \s*className="w-full h-full transition-transform duration-75 ease-out" \s*style=\{\{ transform: `translate\(\$\{beforeTransform\.x\}px, \$\{beforeTransform\.y\}px\) scale\(\$\{beforeTransform\.scale\}\)` \}\}\s*>)'
before_transform_replace = r'<div \n            className="w-full h-full transition-transform duration-75 ease-out" \n            style={{ \n              transform: `translate(${beforeTransform.x}px, ${beforeTransform.y}px) scale(${beforeTransform.scale})`,\n              filter: `brightness(${brightness}%) contrast(${contrast}%)`\n            }}\n          >'
content = re.sub(before_transform_search, before_transform_replace, content)

after_transform_search = r'(<div \s*className="w-full h-full transition-transform duration-75 ease-out" \s*style=\{\{ transform: `translate\(\$\{afterTransform\.x\}px, \$\{afterTransform\.y\}px\) scale\(\$\{afterTransform\.scale\}\)` \}\}\s*>)'
after_transform_replace = r'<div \n            className="w-full h-full transition-transform duration-75 ease-out" \n            style={{ \n              transform: `translate(${afterTransform.x}px, ${afterTransform.y}px) scale(${afterTransform.scale})`,\n              filter: `brightness(${brightness}%) contrast(${contrast}%)`\n            }}\n          >'
content = re.sub(after_transform_search, after_transform_replace, content)

mobile_video_search = r'(<div className="relative flex-1 w-full h-full">)'
mobile_video_replace = r'<div className="relative flex-1 w-full h-full" style={{ filter: `brightness(${brightness}%) contrast(${contrast}%)` }}>'
content = re.sub(mobile_video_search, mobile_video_replace, content)

# Add Filter button to controls
filter_ui = """          <div className="relative">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2.5 rounded-full shadow-lg backdrop-blur-md border transition-all flex items-center justify-center ${showFilters || brightness !== 100 || contrast !== 100 ? 'bg-indigo-600/90 hover:bg-indigo-500 border-white/20 text-white' : 'bg-black/60 hover:bg-black/80 border-white/20 text-white/70 hover:text-white'}`}
              title="Adjust visual filters"
            >
              <SlidersHorizontal size={20} />
            </button>
            
            {showFilters && (
              <div className="absolute bottom-full right-0 mb-2 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl p-4 shadow-2xl w-64 z-50">
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
              </div>
            )}
          </div>
          <button"""

content = content.replace('          <button\n            onClick={handleExportFrame}', filter_ui + '\n            onClick={handleExportFrame}')

with open('app/page.tsx', 'w') as f:
    f.write(content)
