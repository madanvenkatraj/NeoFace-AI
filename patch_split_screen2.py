import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# Fix the wrappers
old_before_wrapper = '<div className="absolute inset-0 w-full h-full overflow-hidden">'
new_before_wrapper = '<div className={`absolute inset-0 w-full h-full overflow-hidden ${isSplitScreen ? "w-1/2 border-r border-white/20" : ""}`} style={isSplitScreen ? { clipPath: "inset(0 0 0 0)" } : {}}>'

content = content.replace(old_before_wrapper, new_before_wrapper, 1) # Only first one


old_after_wrapper_search = r'<div \s*className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none"\s*style=\{\{ clipPath: `inset\(0 \$\{100 - position\}\% 0 0\)` \}\}\s*>'
new_after_wrapper = r'<div className={`absolute inset-0 w-full h-full overflow-hidden pointer-events-none ${isSplitScreen ? "left-1/2 w-1/2" : ""}`} style={isSplitScreen ? { clipPath: "inset(0 0 0 0)" } : { clipPath: `inset(0 ${100 - position}% 0 0)` }}>'
content = re.sub(old_after_wrapper_search, new_after_wrapper, content)

with open('app/page.tsx', 'w') as f:
    f.write(content)
