import re

# Ok, I need to restore <html> and <body> in layout.tsx because Next.js App Router strictly requires them.
with open('app/layout.tsx', 'r') as f:
    content = f.read()

content = content.replace("<div lang=", "<html lang=").replace("</body></div>", "</body></html>")

with open('app/layout.tsx', 'w') as f:
    f.write(content)
