import re

with open('components/NeoFaceStudio.tsx', 'r') as f:
    content = f.read()

old_key = """      if ((e.ctrlKey || e.metaKey) && e.code === 'Enter' && currentStep === 3) {"""
new_key = """      if (e.code === 'KeyL' && (currentStep === 2 || currentStep === 3)) {
        e.preventDefault();
        setShowLandmarks(p => !p);
      }
      if ((e.ctrlKey || e.metaKey) && e.code === 'Enter' && currentStep === 3) {"""

content = content.replace(old_key, new_key)

with open('components/NeoFaceStudio.tsx', 'w') as f:
    f.write(content)
