with open('components/NeoFaceStudio.tsx', 'r') as f:
    content = f.read()

content = content.replace("PlayCircle,", "PlayCircle,\n  Pause,")

with open('components/NeoFaceStudio.tsx', 'w') as f:
    f.write(content)
