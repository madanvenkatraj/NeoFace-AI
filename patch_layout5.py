import re

with open('app/layout.tsx', 'r') as f:
    content = f.read()

content = content.replace("</body>    </div>", "</body>    </html>")

with open('app/layout.tsx', 'w') as f:
    f.write(content)
