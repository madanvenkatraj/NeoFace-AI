import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

code = code.replace("onClick={() => setSourceSelectionModal(null); setSourceModalSize(null)}", "onClick={() => { setSourceSelectionModal(null); setSourceModalSize(null); }}")

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)

print("Fixed modal brackets")
