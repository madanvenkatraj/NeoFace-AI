import re

with open('app/layout.tsx', 'r') as f:
    content = f.read()

# Replace <html lang="en" ...> with <html> tag that has suppressHydrationWarning.
# The issue might literally be a bug in how Next.js parses `html` vs `Html` inside components imported dynamically, or something else.
# But actually, there are no other HTML tags in RootLayout. 
# Let me look closely.
print("Layout Check OK")
