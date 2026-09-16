import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# Replace the existing group
new_buttons = """      {/* Export Frame and Jump Time */}
      {isVideo && (
        <div className="absolute bottom-16 right-4 md:bottom-4 md:right-4 z-40 flex items-center gap-2">
          <div className="bg-black/60 backdrop-blur-md border border-white/20 rounded-full px-2 py-1 flex items-center shadow-lg transition-all focus-within:border-indigo-400">
            <button 
              onClick={() => handleFrameStep('prev')}
              className="text-white/70 hover:text-white p-1 hover:bg-white/10 rounded-full transition-colors"
              title="Previous Frame"
            >
              <ChevronLeft size={16} />
            </button>
            <Clock size={14} className="text-white/70 mx-1" />
            <input 
              type="number"
              step="0.033"
              min="0"
              value={jumpTime}
              onChange={(e) => setJumpTime(e.target.value)}
              onKeyDown={handleJumpTime}
              onBlur={handleJumpTime}
              placeholder="0.0"
              className="bg-transparent text-white w-14 text-sm outline-none placeholder:text-white/30 text-center font-medium"
              title="Jump to second (press Enter)"
            />
            <span className="text-white/50 text-xs mr-1">s</span>
            <button 
              onClick={() => handleFrameStep('next')}
              className="text-white/70 hover:text-white p-1 hover:bg-white/10 rounded-full transition-colors"
              title="Next Frame"
            >
              <ChevronRight size={16} />
            </button>
          </div>
          <button
            onClick={handleExportFrame}
            className="bg-indigo-600/90 hover:bg-indigo-500 text-white p-2.5 rounded-full shadow-lg backdrop-blur-md border border-white/20 transition-all flex items-center justify-center group/btn"
            title="Export current frame as image"
          >
            <Camera size={20} className="group-hover/btn:scale-110 transition-transform" />
          </button>
        </div>
      )}"""

# We'll split the content and reconstruct it
start_marker = "{/* Export Frame and Jump Time */}"
end_marker = "</div>\n  );\n};"

if start_marker in content:
    parts = content.split(start_marker)
    before_content = parts[0]
    after_part = parts[1]
    
    # find the end of the block in after_part
    # The block ends right before </div>\n  );\n};
    end_index = after_part.find("</div>\n  );\n};")
    if end_index != -1:
        content = before_content + new_buttons + "\n\n    </div>\n  );\n};\n"
    
with open('app/page.tsx', 'w') as f:
    f.write(content)
