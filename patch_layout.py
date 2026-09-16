import re

with open('app/layout.tsx', 'r') as f:
    content = f.read()

# Replace <html ...> and </html> with generic <div> or similar, or check if it's the <html> element issue.
# Wait, in Next.js App Router, layout.tsx MUST export a function returning <html> and <body>.
# But the error is "<Html> should not be imported outside of pages/_document".
# Oh wait, there might be a <Html> import somewhere.

# Let's search for "Html" import.
content_check = "next/document" in content
