import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# 1. Add jumpTime state
new_state = "  const [jumpTime, setJumpTime] = useState<string>('');\n"
content = re.sub(r'(const \[mobileView, setMobileView\] = useState<\'before\' \| \'after\'>\(\'after\'\);\n)', r'\1' + new_state, content)

# 2. Add handleJumpTime function
handle_func = """
  const handleJumpTime = (e: React.KeyboardEvent<HTMLInputElement> | React.FocusEvent<HTMLInputElement>) => {
    if ('key' in e && (e as React.KeyboardEvent).key !== 'Enter') return;
    
    const time = parseFloat(jumpTime);
    if (!isNaN(time) && isVideo) {
      if (beforeRef.current) beforeRef.current.currentTime = time;
      if (afterRef.current) afterRef.current.currentTime = time;
      if (mobileVideoRef.current) mobileVideoRef.current.currentTime = time;
    }
  };
"""
content = re.sub(r'(const handleExportFrame = \(\) => \{)', handle_func + r'\n  \1', content)

# 3. Replace the button with the group
old_button = """      {/* Export Frame Button */}
      {isVideo && (
        <button
          onClick={handleExportFrame}
          className="absolute bottom-16 right-4 md:bottom-4 md:right-4 z-40 bg-indigo-600/90 hover:bg-indigo-500 text-white p-2.5 rounded-full shadow-lg backdrop-blur-md border border-white/20 transition-all flex items-center justify-center group/btn"
          title="Export current frame as image"
        >
          <Camera size={20} className="group-hover/btn:scale-110 transition-transform" />
        </button>
      )}"""

new_button = """      {/* Export Frame and Jump Time */}
      {isVideo && (
        <div className="absolute bottom-16 right-4 md:bottom-4 md:right-4 z-40 flex items-center gap-2">
          <div className="bg-black/60 backdrop-blur-md border border-white/20 rounded-full px-3 py-1.5 flex items-center shadow-lg transition-all focus-within:border-indigo-400">
            <Clock size={14} className="text-white/70 mr-1.5" />
            <input 
              type="number"
              step="0.1"
              min="0"
              value={jumpTime}
              onChange={(e) => setJumpTime(e.target.value)}
              onKeyDown={handleJumpTime}
              onBlur={handleJumpTime}
              placeholder="0.0"
              className="bg-transparent text-white w-12 text-sm outline-none placeholder:text-white/30 text-center font-medium"
              title="Jump to second (press Enter)"
            />
            <span className="text-white/50 text-xs ml-0.5">s</span>
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

if old_button in content:
    content = content.replace(old_button, new_button)
else:
    print("Could not find old button pattern!")
    # let's try a regex
    content = re.sub(
        r'\{\/\*\s*Export Frame Button\s*\*\/\}.*?<\/button>\s*\}\)',
        new_button,
        content,
        flags=re.DOTALL
    )

with open('app/page.tsx', 'w') as f:
    f.write(content)
