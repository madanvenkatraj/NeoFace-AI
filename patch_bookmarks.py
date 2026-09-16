import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# 1. Add Bookmark to imports
if "Bookmark" not in content:
    content = re.sub(r'(import \{[^\}]*?)( \} from \'lucide-react\';)', r'\1, Bookmark\2', content)

# 2. Add bookmarks state
state_updates = """  const [isSplitScreen, setIsSplitScreen] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [showMetadata, setShowMetadata] = useState(false);
  const [videoMeta, setVideoMeta] = useState<{width: number, height: number} | null>(null);
  const [bookmarks, setBookmarks] = useState<number[]>([]);"""
content = re.sub(r'(const \[isSplitScreen, setIsSplitScreen\] = useState\(false\);\n  const \[isMuted, setIsMuted\] = useState\(true\);\n  const \[showMetadata, setShowMetadata\] = useState\(false\);\n  const \[videoMeta, setVideoMeta\] = useState<\{width: number, height: number\} \| null>\(null\);)', state_updates, content)


# 3. Add bookmark button
volume_btn = r'(<button\s*onClick=\{\(\) => setIsMuted\(!isMuted\)\}[\s\S]*?</button>)'
bookmark_btn = """\\1
            <button
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

content = re.sub(volume_btn, bookmark_btn, content, count=1)


# 4. Add jump to bookmark function
jump_fn = """
  const jumpToTime = (time: number) => {
    setCurrentTime(time);
    setJumpTime(time.toFixed(2));
    if (beforeRef.current) beforeRef.current.currentTime = time;
    if (afterRef.current) afterRef.current.currentTime = time;
  };
"""

content = content.replace("  const handleTimelineScrub = (e: React.ChangeEvent<HTMLInputElement>) => {", jump_fn + "\n  const handleTimelineScrub = (e: React.ChangeEvent<HTMLInputElement>) => {")

# 5. Add visual markers
timeline = """          <div className="w-full h-1.5 bg-white/20 relative pointer-events-none transition-all group-hover/timeline:h-2">
            <div 
              className="h-full bg-indigo-500 relative"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            >
              <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 w-3 h-3 bg-white rounded-full scale-0 group-hover/timeline:scale-100 transition-transform shadow-lg" />
            </div>
          </div>"""

new_timeline = """          {/* Bookmark Markers */}
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
          ))}

          <div className="w-full h-1.5 bg-white/20 relative pointer-events-none transition-all group-hover/timeline:h-2">
            <div 
              className="h-full bg-indigo-500 relative"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            >
              <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 w-3 h-3 bg-white rounded-full scale-0 group-hover/timeline:scale-100 transition-transform shadow-lg" />
            </div>
          </div>"""

content = content.replace(timeline, new_timeline)

with open('app/page.tsx', 'w') as f:
    f.write(content)
