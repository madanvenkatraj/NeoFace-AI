import sys

with open("components/NeoFaceStudio.tsx", "r") as f:
    code = f.read()

# Remove duplicate state declaration
code = code.replace("  const [showHistory, setShowHistory] = useState(false);\n  const [exportPreset, setExportPreset]", "  const [exportPreset, setExportPreset]")

with open("components/NeoFaceStudio.tsx", "w") as f:
    f.write(code)
print("patched NeoFaceStudio.tsx state")
