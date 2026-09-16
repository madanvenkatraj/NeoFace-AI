import re

with open('components/NeoFaceStudio.tsx', 'r') as f:
    content = f.read()

old_play = """<PlayCircle size={16} className="text-cyan-400" />"""
new_play = """{isPlaying ? <Pause size={16} className="text-cyan-400" /> : <PlayCircle size={16} className="text-cyan-400" />}"""

content = content.replace(old_play, new_play)

# Add Pause to lucide imports if not there
if "Pause" not in content:
    content = content.replace("PlayCircle,", "PlayCircle,\n  Pause,")

with open('components/NeoFaceStudio.tsx', 'w') as f:
    f.write(content)
