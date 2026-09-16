import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# Add playbackRate state
state_updates = """  const [playbackRate, setPlaybackRate] = useState<number>(1);
"""

content = re.sub(r'(const \[currentTime, setCurrentTime\] = useState\(0\);\n)', r'\1' + state_updates, content)

# Add changePlaybackRate handler
handler = """
  const changePlaybackRate = (rate: number) => {
    setPlaybackRate(rate);
    if (beforeRef.current) beforeRef.current.playbackRate = rate;
    if (afterRef.current) afterRef.current.playbackRate = rate;
    if (mobileVideoRef.current) mobileVideoRef.current.playbackRate = rate;
  };
"""

content = re.sub(r'(const handleTimelineScrub = )', handler + r'\n  \1', content)

# Modify the Play/Pause controls to add the dropdown
old_play_button = """          <button
            onClick={togglePlay}
            className="bg-indigo-600/90 hover:bg-indigo-500 text-white p-2.5 rounded-full shadow-lg backdrop-blur-md border border-white/20 transition-all flex items-center justify-center group/btn"
            title={isPlaying ? "Pause" : "Play"}
          >
            {isPlaying ? <Pause size={20} className="group-hover/btn:scale-110 transition-transform" /> : <PlayIcon size={20} className="group-hover/btn:scale-110 transition-transform ml-0.5" />}
          </button>"""

new_play_group = """          <div className="flex items-center gap-1 bg-black/60 backdrop-blur-md border border-white/20 rounded-full p-1 shadow-lg">
            <button
              onClick={togglePlay}
              className="bg-indigo-600/90 hover:bg-indigo-500 text-white p-2 rounded-full transition-all flex items-center justify-center group/btn w-9 h-9"
              title={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? <Pause size={18} className="group-hover/btn:scale-110 transition-transform" /> : <PlayIcon size={18} className="group-hover/btn:scale-110 transition-transform ml-0.5" />}
            </button>
            <div className="relative group/speed">
              <button 
                className="text-white text-xs font-semibold px-2 py-1 rounded hover:bg-white/10 transition-colors h-9 flex items-center justify-center w-10"
                title="Playback Speed"
              >
                {playbackRate}x
              </button>
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-black/80 backdrop-blur-md border border-white/10 rounded-lg overflow-hidden flex-col shadow-xl opacity-0 invisible group-hover/speed:opacity-100 group-hover/speed:visible transition-all flex">
                {[0.5, 1, 2].map((rate) => (
                  <button
                    key={rate}
                    onClick={() => changePlaybackRate(rate)}
                    className={`px-4 py-2 text-xs font-semibold text-center transition-colors hover:bg-white/10 ${playbackRate === rate ? 'text-indigo-400 bg-white/5' : 'text-white'}`}
                  >
                    {rate}x
                  </button>
                ))}
              </div>
            </div>
          </div>"""

content = content.replace(old_play_button, new_play_group)

with open('app/page.tsx', 'w') as f:
    f.write(content)
