import re

with open('app/layout.tsx', 'r') as f:
    content = f.read()

# Replace <html lang="en" className={`${outfit.variable} dark`}>
# with <div lang="en" className={`${outfit.variable} dark`}>
# And </body></html> with </body></div>
# Actually, the error means that somewhere `Html` is imported from `next/document` which is forbidden in App router.

content = content.replace("<html ", "<div ").replace("</html>", "</div>")

with open('app/layout.tsx', 'w') as f:
    f.write(content)
