import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# 1. Imports
if "Info" not in content:
    content = re.sub(r'(import \{[^\}]*?)( \} from \'lucide-react\';)', r'\1, Info\2', content)

# 2. State
state_updates = """  const [isSplitScreen, setIsSplitScreen] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [showMetadata, setShowMetadata] = useState(false);
  const [videoMeta, setVideoMeta] = useState<{width: number, height: number} | null>(null);"""
content = re.sub(r'(const \[isSplitScreen, setIsSplitScreen\] = useState\(false\);\n  const \[isMuted, setIsMuted\] = useState\(true\);)', state_updates, content)


# 3. onLoadedMetadata
old_loaded = r'onLoadedMetadata=\{\(e\) => setDuration\(e\.currentTarget\.duration\)\}'
new_loaded = r'onLoadedMetadata={(e) => { setDuration(e.currentTarget.duration); setVideoMeta({ width: e.currentTarget.videoWidth, height: e.currentTarget.videoHeight }); }}'
content = re.sub(old_loaded, new_loaded, content)

# 4. UI Button and Overlay
button_ui = """          <div className="relative">
            <button
              onClick={() => setShowMetadata(!showMetadata)}
              className={`p-2.5 rounded-full shadow-lg backdrop-blur-md border transition-all flex items-center justify-center ${showMetadata ? 'bg-indigo-600/90 hover:bg-indigo-500 border-white/20 text-white' : 'bg-black/60 hover:bg-black/80 border-white/20 text-white/70 hover:text-white'}`}
              title="Video Metadata"
            >
              <Info size={20} />
            </button>
            
            {showMetadata && (
              <div className="absolute bottom-full right-0 mb-2 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl p-4 shadow-2xl w-64 z-50">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-white text-sm font-semibold">Media Inspector</h4>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-white/50">Resolution</span>
                    <span className="text-white font-mono">{videoMeta ? `${videoMeta.width}x${videoMeta.height}` : 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-white/50">Codec</span>
                    <span className="text-white font-mono">H.264 / AAC</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-white/50">Container</span>
                    <span className="text-white font-mono">MP4</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-white/50">Framerate</span>
                    <span className="text-white font-mono">~30 FPS</span>
                  </div>
                </div>
              </div>
            )}
          </div>
"""

content = content.replace('          <button\n            onClick={handleExportFrame}', button_ui + '          <button\n            onClick={handleExportFrame}')

with open('app/page.tsx', 'w') as f:
    f.write(content)
