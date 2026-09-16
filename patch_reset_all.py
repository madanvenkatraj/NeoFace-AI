import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# 1. Add resetFilters function
state_updates = """  const [saturation, setSaturation] = useState(100);
  const [showFilters, setShowFilters] = useState(false);

  const resetFilters = () => {
    setBrightness(100);
    setContrast(100);
    setSaturation(100);
  };"""

content = re.sub(r'(\s*const \[saturation, setSaturation\] = useState\(100\);\n\s*const \[showFilters, setShowFilters\] = useState\(false\);)', state_updates, content)

# 2. Update the Reset button
old_button = '<button onClick={() => { setBrightness(100); setContrast(100); setSaturation(100); }} className="text-xs text-white/50 hover:text-white transition-colors">Reset</button>'
new_button = '<button onClick={resetFilters} className="text-xs text-white/50 hover:text-white transition-colors">Reset All</button>'

content = content.replace(old_button, new_button)

with open('app/page.tsx', 'w') as f:
    f.write(content)
