import re

with open('app/page.tsx', 'r') as f:
    content = f.read()

# Make sure we add necessary icons if not present
if "ZoomIn" not in content:
    content = re.sub(r'(import \{[^\}]*?)( \} from \'lucide-react\';)', r'\1, ZoomIn, Maximize, Lock, Unlock\2', content)

# 1. State for zoom/pan
state_str = """
  const [syncZoomPan, setSyncZoomPan] = useState(true);
  const [beforeTransform, setBeforeTransform] = useState({ scale: 1, x: 0, y: 0 });
  const [afterTransform, setAfterTransform] = useState({ scale: 1, x: 0, y: 0 });
  const [isDraggingPan, setIsDraggingPan] = useState<'before' | 'after' | 'both' | null>(null);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const handleWheel = (e: React.WheelEvent) => {
    e.stopPropagation();
    const zoomFactor = -e.deltaY * 0.005;
    const isLeft = containerRef.current ? (e.clientX - containerRef.current.getBoundingClientRect().left) / containerRef.current.offsetWidth * 100 < position : true;
    
    if (syncZoomPan) {
      const newScale = Math.max(1, Math.min(beforeTransform.scale + zoomFactor, 10));
      setBeforeTransform(prev => ({ ...prev, scale: newScale }));
      setAfterTransform(prev => ({ ...prev, scale: newScale }));
    } else {
      if (isLeft) {
        setBeforeTransform(prev => ({ ...prev, scale: Math.max(1, Math.min(prev.scale + zoomFactor, 10)) }));
      } else {
        setAfterTransform(prev => ({ ...prev, scale: Math.max(1, Math.min(prev.scale + zoomFactor, 10)) }));
      }
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    // Only pan if not clicking on the slider handle (z-20)
    if ((e.target as HTMLElement).tagName === 'INPUT') return;
    
    const isLeft = containerRef.current ? (e.clientX - containerRef.current.getBoundingClientRect().left) / containerRef.current.offsetWidth * 100 < position : true;
    
    setDragStart({ x: e.clientX, y: e.clientY });
    if (syncZoomPan) {
      setIsDraggingPan('both');
    } else {
      setIsDraggingPan(isLeft ? 'before' : 'after');
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingPan) return;
    const dx = e.clientX - dragStart.x;
    const dy = e.clientY - dragStart.y;
    setDragStart({ x: e.clientX, y: e.clientY });

    if (isDraggingPan === 'both' || isDraggingPan === 'before') {
      setBeforeTransform(prev => ({ ...prev, x: prev.x + dx, y: prev.y + dy }));
    }
    if (isDraggingPan === 'both' || isDraggingPan === 'after') {
      setAfterTransform(prev => ({ ...prev, x: prev.x + dx, y: prev.y + dy }));
    }
  };

  const handleMouseUp = () => setIsDraggingPan(null);

  const resetZoomPan = () => {
    setBeforeTransform({ scale: 1, x: 0, y: 0 });
    setAfterTransform({ scale: 1, x: 0, y: 0 });
  };
"""

content = re.sub(r'(const handleFrameStep =)', state_str + r'\n  \1', content)

# 2. Add containerRef, onWheel, onMouseDown etc to the main desktop container
old_desktop_start = """      {/* --- DESKTOP SLIDER VIEW (hidden on mobile) --- */}
      <div className="hidden md:block absolute inset-0 w-full h-full">"""

new_desktop_start = """      {/* --- DESKTOP SLIDER VIEW (hidden on mobile) --- */}
      <div 
        ref={containerRef}
        className="hidden md:block absolute inset-0 w-full h-full"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >"""

content = content.replace(old_desktop_start, new_desktop_start)

# 3. Wrap Before Media in transform div
old_before = """        {/* Before Media */}
        {isVideo ? (
          <video
            ref={beforeRef}
            src={beforeSrc}
            crossOrigin="anonymous"
            className="absolute inset-0 w-full h-full object-contain"
            muted
            loop
            onPlay={() => syncVideos('play')}
            onPause={() => syncVideos('pause')}
            onSeeked={(e) => { if (afterRef.current) afterRef.current.currentTime = e.currentTarget.currentTime; }}
            controls
          />
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={beforeSrc} alt="Original" crossOrigin="anonymous" className="absolute inset-0 w-full h-full object-contain" />
        )}"""

new_before = """        {/* Before Media */}
        <div className="absolute inset-0 w-full h-full overflow-hidden">
          <div 
            className="w-full h-full transition-transform duration-75 ease-out" 
            style={{ transform: `translate(${beforeTransform.x}px, ${beforeTransform.y}px) scale(${beforeTransform.scale})` }}
          >
            {isVideo ? (
              <video
                ref={beforeRef}
                src={beforeSrc}
                crossOrigin="anonymous"
                className="w-full h-full object-contain pointer-events-none"
                muted
                loop
                onPlay={() => syncVideos('play')}
                onPause={() => syncVideos('pause')}
                onSeeked={(e) => { if (afterRef.current) afterRef.current.currentTime = e.currentTarget.currentTime; }}
              />
            ) : (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={beforeSrc} alt="Original" crossOrigin="anonymous" className="w-full h-full object-contain pointer-events-none" />
            )}
          </div>
        </div>"""

content = content.replace(old_before, new_before)

# 4. Wrap After Media in transform div
old_after = """        {/* After Media */}
        {isVideo ? (
          <video
            ref={afterRef}
            src={afterSrc}
            crossOrigin="anonymous"
            className="absolute inset-0 w-full h-full object-contain pointer-events-none"
            style={{ clipPath: `inset(0 ${100 - position}% 0 0)` }}
            muted
            loop
          />
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img 
            src={afterSrc} 
            alt="Processed" 
            crossOrigin="anonymous"
            className="absolute inset-0 w-full h-full object-contain pointer-events-none" 
            style={{ clipPath: `inset(0 ${100 - position}% 0 0)` }}
          />
        )}"""

new_after = """        {/* After Media */}
        <div 
          className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none"
          style={{ clipPath: `inset(0 ${100 - position}% 0 0)` }}
        >
          <div 
            className="w-full h-full transition-transform duration-75 ease-out" 
            style={{ transform: `translate(${afterTransform.x}px, ${afterTransform.y}px) scale(${afterTransform.scale})` }}
          >
            {isVideo ? (
              <video
                ref={afterRef}
                src={afterSrc}
                crossOrigin="anonymous"
                className="w-full h-full object-contain"
                muted
                loop
              />
            ) : (
              // eslint-disable-next-line @next/next/no-img-element
              <img 
                src={afterSrc} 
                alt="Processed" 
                crossOrigin="anonymous"
                className="w-full h-full object-contain" 
              />
            )}
          </div>
        </div>"""

content = content.replace(old_after, new_after)

# 5. Add Sync Zoom/Pan toggle and Reset button to the controls
old_controls = """          <button
            onClick={handleExportFrame}
            className="bg-indigo-600/90 hover:bg-indigo-500 text-white p-2.5 rounded-full shadow-lg backdrop-blur-md border border-white/20 transition-all flex items-center justify-center group/btn"
            title="Export current frame as image"
          >
            <Camera size={20} className="group-hover/btn:scale-110 transition-transform" />
          </button>"""

new_controls = """          <button
            onClick={() => setSyncZoomPan(!syncZoomPan)}
            className={`p-2.5 rounded-full shadow-lg backdrop-blur-md border transition-all flex items-center justify-center ${syncZoomPan ? 'bg-emerald-600/90 hover:bg-emerald-500 border-white/20 text-white' : 'bg-black/60 hover:bg-black/80 border-white/20 text-white/70 hover:text-white'}`}
            title={syncZoomPan ? "Unsync Zoom/Pan" : "Sync Zoom/Pan"}
          >
            {syncZoomPan ? <Lock size={20} /> : <Unlock size={20} />}
          </button>
          
          {(beforeTransform.scale > 1 || afterTransform.scale > 1 || beforeTransform.x !== 0 || afterTransform.x !== 0) && (
            <button
              onClick={resetZoomPan}
              className="bg-black/60 hover:bg-black/80 text-white/70 hover:text-white p-2.5 rounded-full shadow-lg backdrop-blur-md border border-white/20 transition-all flex items-center justify-center"
              title="Reset Zoom & Pan"
            >
              <Maximize size={20} />
            </button>
          )}

          <button
            onClick={handleExportFrame}
            className="bg-indigo-600/90 hover:bg-indigo-500 text-white p-2.5 rounded-full shadow-lg backdrop-blur-md border border-white/20 transition-all flex items-center justify-center group/btn"
            title="Export current frame as image"
          >
            <Camera size={20} className="group-hover/btn:scale-110 transition-transform" />
          </button>"""

content = content.replace(old_controls, new_controls)

with open('app/page.tsx', 'w') as f:
    f.write(content)
