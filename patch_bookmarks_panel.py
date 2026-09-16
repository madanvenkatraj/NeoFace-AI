import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# 1. Imports
content = re.sub(r'(import \{[^\}]*?)( \} from \'lucide-react\';)', r'\1, List, Trash2\2', content)

# 2. Add state
state_updates = """  const [isMuted, setIsMuted] = useState(true);
  const [showMetadata, setShowMetadata] = useState(false);
  const [videoMeta, setVideoMeta] = useState<{width: number, height: number} | null>(null);
  const [bookmarks, setBookmarks] = useState<number[]>([]);
  const [showBookmarksPanel, setShowBookmarksPanel] = useState(false);
  
  const removeBookmark = (time: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setBookmarks(bookmarks.filter(b => b !== time));
  };"""

content = re.sub(
    r'const \[isMuted, setIsMuted\] = useState\(true\);\s*const \[showMetadata, setShowMetadata\] = useState\(false\);\s*const \[videoMeta, setVideoMeta\] = useState<\{width: number, height: number\} \| null>\(null\);\s*const \[bookmarks, setBookmarks\] = useState<number\[\]>\(\[\]\);',
    state_updates,
    content
)

# 3. Add UI Panel
bookmark_btn_regex = r'(<button\s*onClick=\{\(\) => \{\s*if \(\!bookmarks\.includes\(currentTime\)\) \{\s*setBookmarks\(\[\.\.\.bookmarks, currentTime\]\.sort\(\(a, b\) => a - b\)\);\s*\}\s*\}\}\s*className="text-white/70 hover:text-white p-2 hover:bg-white/10 rounded-full transition-colors flex items-center justify-center w-9 h-9 relative"\s*title="Add Marker"\s*>\s*<Bookmark size=\{18\} />\s*\{bookmarks\.includes\(currentTime\) && \(\s*<div className="absolute top-1 right-1 w-2 h-2 bg-indigo-500 rounded-full border border-black/50" />\s*\)\}\s*</button>)'

bookmark_replacement = """\\1
            <div className="relative">
              <button
                onClick={() => setShowBookmarksPanel(!showBookmarksPanel)}
                className={`p-2 rounded-full transition-all flex items-center justify-center w-9 h-9 ${showBookmarksPanel ? 'bg-indigo-600 text-white shadow-lg' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
                title="Markers List"
              >
                <List size={18} />
                {bookmarks.length > 0 && (
                  <span className="absolute top-0 right-0 bg-indigo-500 text-[9px] font-bold w-3.5 h-3.5 flex items-center justify-center rounded-full border border-black/50">{bookmarks.length}</span>
                )}
              </button>
              
              {showBookmarksPanel && (
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl p-3 shadow-2xl w-48 z-50 flex flex-col max-h-64">
                  <div className="flex justify-between items-center mb-2 px-1">
                    <h4 className="text-white text-xs font-semibold">Saved Markers</h4>
                    <span className="text-white/40 text-[10px] font-mono">{bookmarks.length}</span>
                  </div>
                  <div className="overflow-y-auto pr-1 space-y-1 flex-1 custom-scrollbar">
                    {bookmarks.length === 0 ? (
                      <div className="text-white/40 text-[10px] text-center py-4 italic">No markers added</div>
                    ) : (
                      bookmarks.map((time) => (
                        <div 
                          key={time}
                          onClick={() => jumpToTime(time)}
                          className="flex items-center justify-between p-1.5 hover:bg-white/10 rounded-lg cursor-pointer group transition-colors"
                        >
                          <span className="text-white/80 group-hover:text-white font-mono text-[11px] font-medium">
                            {time.toFixed(2)}s
                          </span>
                          <button 
                            onClick={(e) => removeBookmark(time, e)}
                            className="text-white/30 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all p-1 rounded hover:bg-white/5"
                            title="Remove marker"
                          >
                            <Trash2 size={12} />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>"""

content = re.sub(bookmark_btn_regex, bookmark_replacement, content)

with open('app/page.tsx', 'w') as f:
    f.write(content)
