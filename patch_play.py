import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# Add isPlaying state
if "const [isPlaying, setIsPlaying] = useState(false);" not in content:
    state_str = "  const [isPlaying, setIsPlaying] = useState(false);\n"
    content = re.sub(r'(const \[mobileView, setMobileView\] = useState<\'before\' \| \'after\'>\(\'after\'\);\n)', r'\1' + state_str, content)

# Add play/pause toggle function
toggle_func = """
  const togglePlay = () => {
    if (!isVideo) return;
    if (isPlaying) {
      beforeRef.current?.pause();
      afterRef.current?.pause();
      mobileVideoRef.current?.pause();
    } else {
      beforeRef.current?.play().catch(() => {});
      afterRef.current?.play().catch(() => {});
      mobileVideoRef.current?.play().catch(() => {});
    }
    setIsPlaying(!isPlaying);
  };
"""
if "const togglePlay = () => {" not in content:
    content = re.sub(r'(const syncVideos = \(action: \'play\' \| \'pause\'\) => \{)', toggle_func + r'\n  \1', content)

# Add Play/Pause to imports if not there
if "Pause," not in content:
    content = re.sub(r'(import \{[^\}]*?)( \} from \'lucide-react\';)', r'\1, Pause, Play as PlayIcon\2', content)

# Update syncVideos to set isPlaying
sync_videos_update = """  const syncVideos = (action: 'play' | 'pause') => {
    if (!isVideo || !beforeRef.current || !afterRef.current) return;
    if (action === 'play') {
      setIsPlaying(true);
      beforeRef.current.play().catch(() => {});
      afterRef.current.play().catch(() => {});
    } else {
      setIsPlaying(false);
      beforeRef.current.pause();
      afterRef.current.pause();
    }
  };"""

content = re.sub(r'const syncVideos = \(action: \'play\' \| \'pause\'\) => \{.*?\};', sync_videos_update, content, flags=re.DOTALL)

# Add Play/Pause button to controls
old_controls = """          <div className="bg-black/60 backdrop-blur-md border border-white/20 rounded-full px-2 py-1 flex items-center shadow-lg transition-all focus-within:border-indigo-400">"""

new_controls = """          <button
            onClick={togglePlay}
            className="bg-indigo-600/90 hover:bg-indigo-500 text-white p-2.5 rounded-full shadow-lg backdrop-blur-md border border-white/20 transition-all flex items-center justify-center group/btn"
            title={isPlaying ? "Pause" : "Play"}
          >
            {isPlaying ? <Pause size={20} className="group-hover/btn:scale-110 transition-transform" /> : <PlayIcon size={20} className="group-hover/btn:scale-110 transition-transform ml-0.5" />}
          </button>
          
          <div className="bg-black/60 backdrop-blur-md border border-white/20 rounded-full px-2 py-1 flex items-center shadow-lg transition-all focus-within:border-indigo-400">"""

if "onClick={togglePlay}" not in content:
    content = content.replace(old_controls, new_controls)

with open('app/page.tsx', 'w') as f:
    f.write(content)
