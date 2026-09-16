import re

with open('components/NeoFaceStudio.tsx', 'r') as f:
    content = f.read()

content = content.replace("const handleTargetUpload =", "const handleFileUpload =")

with open('components/NeoFaceStudio.tsx', 'w') as f:
    f.write(content)
