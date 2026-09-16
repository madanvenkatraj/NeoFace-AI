import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# 1. State
state_updates = """  const [bookmarks, setBookmarks] = useState<{time: number, type: 'default' | 'good' | 'error'}[]>([]);
  const [showBookmarksPanel, setShowBookmarksPanel] = useState(false);
  const [isTrimMode, setIsTrimMode] = useState(false);
  const [trimStart, setTrimStart] = useState<number>(0);
  const [trimEnd, setTrimEnd] = useState<number>(0);"""

content = content.replace("  const [bookmarks, setBookmarks] = useState<{time: number, type: 'default' | 'good' | 'error'}[]>([]);\n  const [showBookmarksPanel, setShowBookmarksPanel] = useState(false);", state_updates)

# 2. Add button in controls
btn_regex = r'(<button\s*onClick=\{\(\) => setShowBookmarksPanel\(\!showBookmarksPanel\)\}[\s\S]*?</button>\s*\{showBookmarksPanel && \([\s\S]*?</div>\s*\)\}\s*</div>)'

btn_replacement = """\\1
            <button
              onClick={() => {
                if (!isTrimMode) {
                  setTrimStart(Math.max(0, currentTime - 2));
                  setTrimEnd(Math.min(duration, currentTime + 2));
                }
                setIsTrimMode(!isTrimMode);
              }}
              className={`p-2 rounded-full transition-all flex items-center justify-center w-9 h-9 ${isTrimMode ? 'bg-indigo-600 text-white shadow-lg' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
              title="Export Clip"
            >
              <Scissors size={18} />
            </button>"""

content = re.sub(btn_regex, btn_replacement, content)

# 3. Add Trim UI panel
timeline_wrapper = r'(<div \s*className="absolute bottom-0 left-0 w-full h-3 z-40 group/timeline flex items-end"\s*onMouseMove=\{handleTimelineMouseMove\}\s*onMouseLeave=\{handleTimelineMouseLeave\}\s*>)'

trim_ui = """
      {/* Trim / Export UI */}
      {isTrimMode && (
        <div className="absolute bottom-20 left-1/2 -translate-x-1/2 bg-black/80 backdrop-blur-xl rounded-2xl p-3 shadow-2xl flex items-center gap-4 z-50 border border-white/20">
          <div className="flex flex-col">
            <span className="text-[10px] text-white/50 uppercase tracking-wider font-semibold mb-1">Start (s)</span>
            <input 
              type="number" 
              step="0.1" 
              min={0}
              max={trimEnd}
              value={trimStart} 
              onChange={e => setTrimStart(Number(e.target.value))} 
              className="w-16 bg-white/5 border border-white/10 rounded px-2 py-1 text-white text-xs focus:outline-none focus:border-indigo-500 transition-colors font-mono" 
            />
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-white/50 uppercase tracking-wider font-semibold mb-1">End (s)</span>
            <input 
              type="number" 
              step="0.1"
              min={trimStart}
              max={duration}
              value={trimEnd} 
              onChange={e => setTrimEnd(Number(e.target.value))} 
              className="w-16 bg-white/5 border border-white/10 rounded px-2 py-1 text-white text-xs focus:outline-none focus:border-indigo-500 transition-colors font-mono" 
            />
          </div>
          <div className="h-8 w-px bg-white/20 mx-1"></div>
          <button 
            onClick={() => {
              const cmd = `ffmpeg -i input.mp4 -ss ${trimStart.toFixed(2)} -to ${trimEnd.toFixed(2)} -c:v copy -c:a copy export_clip.mp4`;
              navigator.clipboard.writeText(cmd);
              alert(`FFMPEG Command copied to clipboard:\\n${cmd}`);
              setIsTrimMode(false);
            }} 
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all shadow-lg hover:shadow-indigo-500/25"
          >
            <Download size={14} /> Export FFMPEG
          </button>
          <button onClick={() => setIsTrimMode(false)} className="text-white/50 hover:text-white p-2 rounded-full hover:bg-white/10 transition-colors ml-1">
            <X size={16} />
          </button>
        </div>
      )}

      \\1"""

content = re.sub(timeline_wrapper, trim_ui, content)

# 4. Add Trim Region Highlight to Timeline
progress_bar = r'(<div \s*className="h-full bg-indigo-500 relative"\s*style=\{\{ width: `\$\{\(currentTime / duration\) \* 100\}%` \}\}\s*>)'

highlight = """          {/* Trim Region Highlight */}
          {isTrimMode && (
            <div 
              className="absolute bottom-0 h-full bg-indigo-500/40 border-l border-r border-indigo-400 z-[45] pointer-events-none" 
              style={{ left: `${(trimStart / duration) * 100}%`, width: `${((trimEnd - trimStart) / duration) * 100}%` }} 
            />
          )}
          
          \\1"""

content = re.sub(progress_bar, highlight, content)

with open('app/page.tsx', 'w') as f:
    f.write(content)

