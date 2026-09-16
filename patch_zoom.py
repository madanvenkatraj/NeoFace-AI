import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# Replace the conditional resetZoomPan button with a permanent one
old_button = """          {(beforeTransform.scale > 1 || afterTransform.scale > 1 || beforeTransform.x !== 0 || afterTransform.x !== 0) && (
            <button
              onClick={resetZoomPan}
              className="bg-black/60 hover:bg-black/80 text-white/70 hover:text-white p-2.5 rounded-full shadow-lg backdrop-blur-md border border-white/20 transition-all flex items-center justify-center"
              title="Reset Zoom & Pan"
            >
              <Maximize size={20} />
            </button>
          )}"""

new_button = """          <button
            onClick={resetZoomPan}
            disabled={beforeTransform.scale === 1 && afterTransform.scale === 1 && beforeTransform.x === 0 && afterTransform.x === 0}
            className={`p-2.5 rounded-full shadow-lg backdrop-blur-md border border-white/20 transition-all flex items-center justify-center ${
              (beforeTransform.scale > 1 || afterTransform.scale > 1 || beforeTransform.x !== 0 || afterTransform.x !== 0) 
                ? 'bg-black/60 hover:bg-black/80 text-white hover:text-white' 
                : 'bg-black/40 text-white/30 cursor-not-allowed'
            }`}
            title="Zoom to Fit"
          >
            <Maximize size={20} />
          </button>"""

if old_button in content:
    content = content.replace(old_button, new_button)
else:
    # use regex
    search = r'\{\(beforeTransform\.scale > 1 \|\| afterTransform\.scale > 1 \|\| beforeTransform\.x !== 0 \|\| afterTransform\.x !== 0\) && \(\s*<button\s*onClick=\{resetZoomPan\}[\s\S]*?<Maximize size=\{20\} />\s*</button>\s*\)\}'
    content = re.sub(search, new_button, content)

with open('app/page.tsx', 'w') as f:
    f.write(content)
