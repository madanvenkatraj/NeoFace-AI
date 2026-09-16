with open('components/NeoFaceStudio.tsx', 'r') as f:
    content = f.read()

if "Zap," not in content:
    content = content.replace("  SaveAll\n}", "  SaveAll,\n  Zap\n}")

with open('components/NeoFaceStudio.tsx', 'w') as f:
    f.write(content)
