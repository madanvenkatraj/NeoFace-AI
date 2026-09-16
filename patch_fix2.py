import re

with open('components/NeoFaceStudio.tsx', 'r') as f:
    content = f.read()

content = re.sub(r'\}, \[currentStep, mappedFaces\]\);\s*setTargetMedia\(file\);', '}, [currentStep, mappedFaces]);\n\n  const handleTargetUpload = (e: React.ChangeEvent<HTMLInputElement>) => {\n    const file = e.target.files?.[0];\n    if (file) {\n      setTargetMedia(file);', content)

with open('components/NeoFaceStudio.tsx', 'w') as f:
    f.write(content)
