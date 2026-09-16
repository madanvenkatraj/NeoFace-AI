import re

with open('components/NeoFaceStudio.tsx', 'r') as f:
    content = f.read()

# Fix imports
content = content.replace("  SlidersHorizontal\n} from 'lucide-react';", "  SlidersHorizontal,\n  Save,\n  Keyboard,\n  Focus,\n  FolderHeart,\n  MonitorPlay\n} from 'lucide-react';")

# Extract the useEffect and place it after handleStartProcessing
effect_match = re.search(r'  // Keyboard Shortcuts\n  useEffect\(\(\) => \{.*?\n  \}, \[currentStep, mappedFaces\]\);\n', content, re.DOTALL)
if effect_match:
    effect_code = effect_match.group(0)
    # Remove it from where it is
    content = content.replace(effect_code, "")
    
    # Place it after handleStartProcessing
    target = r'      if (currentP < 20) setCurrentProcessStep\(0\);.*?    \}, 100\);\n  \};\n'
    content = re.sub(target, lambda m: m.group(0) + '\n' + effect_code, content, flags=re.DOTALL)

with open('components/NeoFaceStudio.tsx', 'w') as f:
    f.write(content)
