import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

content = content.replace("History, RefreshCw, X, Clock,", "History, RefreshCw, X, Clock, Settings, Bell,")

with open('app/page.tsx', 'w') as f:
    f.write(content)
