import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# Add SplitSquare to imports
if "SplitSquareHorizontal" not in content:
    content = re.sub(r'(import \{[^\}]*?)( \} from \'lucide-react\';)', r'\1, Columns\2', content)

# Add state
state_updates = """  const [isSplitScreen, setIsSplitScreen] = useState(false);"""
content = re.sub(r'(const \[showFilters, setShowFilters\] = useState\(false\);\n)', r'\1' + state_updates + '\n', content)

# Update structure logic for split screen
structure_search = r'(<div className="absolute inset-0 w-full h-full overflow-hidden">[\s\S]*?)({/\* Slider Handle \*/})'

def structure_replace(match):
    original_html = match.group(1)
    # The original HTML has the before and after video wrappers.
    # We will conditionally apply clip-path vs flex depending on isSplitScreen
    
    # We need to replace the outermost div and its contents conditionally
    # We'll use a regex to grab the two inner divs (before and after)
    inner_divs_match = re.search(r'<div className="absolute inset-0 w-full h-full overflow-hidden">\s*(<div.*?</div>\s*</div>\s*</div>)\s*(<div.*?</div>\s*</div>\s*</div>)\s*</div>', original_html, re.DOTALL)
    
    if inner_divs_match:
        before_div = inner_divs_match.group(1)
        after_div = inner_divs_match.group(2)
        return """
        {isSplitScreen ? (
          <div className="absolute inset-0 w-full h-full flex bg-black">
            <div className="flex-1 h-full relative overflow-hidden border-r border-white/20">
""" + before_div.replace('style={{ clipPath: `inset(0 ${100 - position}% 0 0)` }}', '') + """
              <div className="absolute top-4 left-4 bg-black/60 text-white px-3 py-1 rounded-md text-sm font-medium backdrop-blur-sm pointer-events-none shadow-sm z-30">Original</div>
            </div>
            <div className="flex-1 h-full relative overflow-hidden">
""" + after_div.replace('style={{ clipPath: `inset(0 0 0 ${position}%)` }}', '') + """
              <div className="absolute top-4 right-4 bg-black/60 text-white px-3 py-1 rounded-md text-sm font-medium backdrop-blur-sm pointer-events-none shadow-sm z-30">Processed</div>
            </div>
          </div>
        ) : (
""" + original_html + """
        )}
""" + match.group(2)
    return match.group(0)

# The structure replacement above is tricky because the inner divs contain the transform divs.
# Let's use a simpler approach: just modify the inline styles and classes dynamically.

before_wrapper_search = r'<div \s*className="absolute inset-0 w-full h-full overflow-hidden"\s*style=\{\{ clipPath: `inset\(0 \$\{100 - position\}\% 0 0\)` \}\}\s*>'
before_wrapper_replace = r'<div className={`absolute inset-0 w-full h-full overflow-hidden ${isSplitScreen ? "w-1/2 border-r border-white/20" : ""}`} style={isSplitScreen ? {} : { clipPath: `inset(0 ${100 - position}% 0 0)` }}>'
content = re.sub(before_wrapper_search, before_wrapper_replace, content)

after_wrapper_search = r'<div \s*className="absolute inset-0 w-full h-full overflow-hidden"\s*style=\{\{ clipPath: `inset\(0 0 0 \$\{position\}\%\)` \}\}\s*>'
after_wrapper_replace = r'<div className={`absolute inset-0 w-full h-full overflow-hidden ${isSplitScreen ? "left-1/2 w-1/2" : ""}`} style={isSplitScreen ? {} : { clipPath: `inset(0 0 0 ${position}%)` }}>'
content = re.sub(after_wrapper_search, after_wrapper_replace, content)

# Hide slider handle and input when in split screen
slider_handle_search = r'({/\* Slider Handle \*/}\s*<div \s*className="absolute top-0 bottom-0 w-1 bg-white cursor-ew-resize z-10 pointer-events-none")'
slider_handle_replace = r'{!isSplitScreen && (\n          <>\n            {/* Slider Handle */}\n            <div className="absolute top-0 bottom-0 w-1 bg-white cursor-ew-resize z-10 pointer-events-none"'
content = re.sub(slider_handle_search, slider_handle_replace, content)

input_search = r'(<input \s*type="range"\s*min=\{0\}\s*max=\{100\}\s*value=\{position\}\s*onChange=\{\(e\) => setPosition\(Number\(e\.target\.value\)\)\}\s*className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-20"\s*/>)'
input_replace = r'\1\n          </>\n        )}'
content = re.sub(input_search, input_replace, content)


# Add Split Screen button to controls
button_ui = """          <button
            onClick={() => setIsSplitScreen(!isSplitScreen)}
            className={`p-2.5 rounded-full shadow-lg backdrop-blur-md border transition-all flex items-center justify-center ${isSplitScreen ? 'bg-indigo-600/90 hover:bg-indigo-500 border-white/20 text-white' : 'bg-black/60 hover:bg-black/80 border-white/20 text-white/70 hover:text-white'}`}
            title={isSplitScreen ? "Exit Split Screen" : "Split Screen"}
          >
            <Columns size={20} />
          </button>
"""

content = content.replace('          <button\n            onClick={handleExportFrame}', button_ui + '          <button\n            onClick={handleExportFrame}')

with open('app/page.tsx', 'w') as f:
    f.write(content)
