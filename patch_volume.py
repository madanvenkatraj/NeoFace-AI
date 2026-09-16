import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# 1. Imports
if "Volume2" not in content:
    content = re.sub(r'(import \{[^\}]*?)( \} from \'lucide-react\';)', r'\1, Volume2, VolumeX\2', content)

# 2. State
state_updates = """  const [isSplitScreen, setIsSplitScreen] = useState(false);
  const [isMuted, setIsMuted] = useState(true);"""
content = re.sub(r'(const \[isSplitScreen, setIsSplitScreen\] = useState\(false\);)', state_updates, content)

# 3. Muted tags
content = re.sub(r'(\s+)muted(\s+loop)', r'\1muted={isMuted}\2', content)

# 4. UI Button
play_btn = r'(<button\s*onClick=\{togglePlay\}[\s\S]*?</button>)'
volume_btn = """\\1
            <button
              onClick={() => setIsMuted(!isMuted)}
              className="text-white/70 hover:text-white p-2 hover:bg-white/10 rounded-full transition-colors flex items-center justify-center w-9 h-9"
              title={isMuted ? "Unmute" : "Mute"}
            >
              {isMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
            </button>"""

content = re.sub(play_btn, volume_btn, content, count=1)

with open('app/page.tsx', 'w') as f:
    f.write(content)
