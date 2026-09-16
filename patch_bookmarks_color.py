import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# 1. State updates
state_old = """  const [videoMeta, setVideoMeta] = useState<{width: number, height: number} | null>(null);
  const [bookmarks, setBookmarks] = useState<number[]>([]);
  const [showBookmarksPanel, setShowBookmarksPanel] = useState(false);
  
  const removeBookmark = (time: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setBookmarks(bookmarks.filter(b => b !== time));
  };"""

state_new = """  const [videoMeta, setVideoMeta] = useState<{width: number, height: number} | null>(null);
  const [bookmarks, setBookmarks] = useState<{time: number, type: 'default' | 'good' | 'error'}[]>([]);
  const [showBookmarksPanel, setShowBookmarksPanel] = useState(false);
  
  const removeBookmark = (time: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setBookmarks(bookmarks.filter(b => b.time !== time));
  };

  const addMarker = (type: 'default' | 'good' | 'error') => {
    const existingIndex = bookmarks.findIndex(b => b.time === currentTime);
    if (existingIndex >= 0) {
      const newBookmarks = [...bookmarks];
      newBookmarks[existingIndex] = { time: currentTime, type };
      setBookmarks(newBookmarks);
    } else {
      setBookmarks([...bookmarks, { time: currentTime, type }].sort((a, b) => a.time - b.time));
    }
  };

  const updateMarkerType = (time: number, type: 'default' | 'good' | 'error') => {
    setBookmarks(bookmarks.map(b => b.time === time ? { ...b, type } : b));
  };"""

content = content.replace(state_old, state_new)

# 2. Add Marker Button
btn_old = """            <button
              onClick={() => {
                if (!bookmarks.includes(currentTime)) {
                  setBookmarks([...bookmarks, currentTime].sort((a, b) => a - b));
                }
              }}
              className="text-white/70 hover:text-white p-2 hover:bg-white/10 rounded-full transition-colors flex items-center justify-center w-9 h-9 relative"
              title="Add Marker"
            >
              <Bookmark size={18} />
              {bookmarks.includes(currentTime) && (
                <div className="absolute top-1 right-1 w-2 h-2 bg-indigo-500 rounded-full border border-black/50" />
              )}
            </button>"""

btn_new = """            <div className="relative group/marker">
              <button
                onClick={() => addMarker('default')}
                className="text-white/70 hover:text-white p-2 hover:bg-white/10 rounded-full transition-colors flex items-center justify-center w-9 h-9 relative"
                title="Add Marker"
              >
                <Bookmark size={18} />
                {bookmarks.some(b => b.time === currentTime) && (
                  <div className={`absolute top-1 right-1 w-2 h-2 rounded-full border border-black/50 ${
                    bookmarks.find(b => b.time === currentTime)?.type === 'good' ? 'bg-green-500' :
                    bookmarks.find(b => b.time === currentTime)?.type === 'error' ? 'bg-red-500' :
                    'bg-indigo-500'
                  }`} />
                )}
              </button>
              
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-black/80 backdrop-blur-md border border-white/10 rounded-lg shadow-xl opacity-0 invisible group-hover/marker:opacity-100 group-hover/marker:visible transition-all flex flex-col overflow-hidden w-28 z-50">
                <button 
                  onClick={() => addMarker('default')}
                  className="px-3 py-2 text-xs font-semibold text-white hover:bg-indigo-500/50 flex items-center gap-2 transition-colors"
                >
                  <div className="w-2 h-2 rounded-full bg-indigo-500" /> Default
                </button>
                <button 
                  onClick={() => addMarker('good')}
                  className="px-3 py-2 text-xs font-semibold text-white hover:bg-green-500/50 flex items-center gap-2 transition-colors"
                >
                  <div className="w-2 h-2 rounded-full bg-green-500" /> Good
                </button>
                <button 
                  onClick={() => addMarker('error')}
                  className="px-3 py-2 text-xs font-semibold text-white hover:bg-red-500/50 flex items-center gap-2 transition-colors"
                >
                  <div className="w-2 h-2 rounded-full bg-red-500" /> Error
                </button>
              </div>
            </div>"""

content = content.replace(btn_old, btn_new)

# 3. Markers Panel update
panel_old = """                      bookmarks.map((time) => (
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
                      ))"""

panel_new = """                      bookmarks.map((bm) => (
                        <div 
                          key={bm.time}
                          onClick={() => jumpToTime(bm.time)}
                          className="flex items-center justify-between p-1.5 hover:bg-white/10 rounded-lg cursor-pointer group transition-colors"
                        >
                          <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${
                              bm.type === 'good' ? 'bg-green-500' :
                              bm.type === 'error' ? 'bg-red-500' :
                              'bg-indigo-500'
                            }`} />
                            <span className="text-white/80 group-hover:text-white font-mono text-[11px] font-medium">
                              {bm.time.toFixed(2)}s
                            </span>
                          </div>
                          <div className="flex items-center gap-0.5">
                            <button 
                              onClick={(e) => { e.stopPropagation(); updateMarkerType(bm.time, bm.type === 'good' ? 'default' : 'good'); }}
                              className="w-5 h-5 rounded hover:bg-white/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                              title="Toggle Good"
                            ><div className={`w-1.5 h-1.5 rounded-full ${bm.type === 'good' ? 'bg-green-400' : 'bg-green-500/40'}`} /></button>
                            <button 
                              onClick={(e) => { e.stopPropagation(); updateMarkerType(bm.time, bm.type === 'error' ? 'default' : 'error'); }}
                              className="w-5 h-5 rounded hover:bg-white/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                              title="Toggle Error"
                            ><div className={`w-1.5 h-1.5 rounded-full ${bm.type === 'error' ? 'bg-red-400' : 'bg-red-500/40'}`} /></button>
                            <button 
                              onClick={(e) => removeBookmark(bm.time, e)}
                              className="text-white/30 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all p-1 rounded hover:bg-white/5 ml-0.5"
                              title="Remove marker"
                            >
                              <Trash2 size={12} />
                            </button>
                          </div>
                        </div>
                      ))"""

content = content.replace(panel_old, panel_new)

# 4. Timeline markers update
timeline_old = """          {/* Bookmark Markers */}
          {bookmarks.map((time) => (
            <div
              key={time}
              onClick={(e) => {
                e.stopPropagation();
                jumpToTime(time);
              }}
              className="absolute bottom-0 w-1.5 h-3 bg-white hover:bg-indigo-400 cursor-pointer z-[60] transition-colors rounded-t-sm"
              style={{ left: `${(time / duration) * 100}%`, transform: 'translateX(-50%)' }}
              title={`Jump to ${time.toFixed(2)}s`}
            />
          ))}"""

timeline_new = """          {/* Bookmark Markers */}
          {bookmarks.map((bm) => (
            <div
              key={bm.time}
              onClick={(e) => {
                e.stopPropagation();
                jumpToTime(bm.time);
              }}
              className={`absolute bottom-0 w-1.5 h-3 cursor-pointer z-[60] transition-colors rounded-t-sm hover:brightness-125 ${
                bm.type === 'good' ? 'bg-green-500' :
                bm.type === 'error' ? 'bg-red-500' :
                'bg-white hover:bg-indigo-400'
              }`}
              style={{ left: `${(bm.time / duration) * 100}%`, transform: 'translateX(-50%)' }}
              title={`${bm.type === 'default' ? 'Marker' : bm.type === 'good' ? 'Good' : 'Error'}: ${bm.time.toFixed(2)}s`}
            />
          ))}"""

content = content.replace(timeline_old, timeline_new)

with open('app/page.tsx', 'w') as f:
    f.write(content)

