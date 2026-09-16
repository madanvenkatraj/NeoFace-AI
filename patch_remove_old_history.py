import sys

with open("components/NeoFaceStudio.tsx", "r") as f:
    code = f.read()

import re
code = re.sub(r'      \{\/\* History Panel \*\/\}.*?      </AnimatePresence>\n', '', code, flags=re.DOTALL)

with open("components/NeoFaceStudio.tsx", "w") as f:
    f.write(code)
print("patched NeoFaceStudio.tsx to remove old history panel")
