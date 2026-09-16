import re

with open('app/page.tsx', 'r') as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if "const MediaCompareSlider = " in line:
        start_idx = i
        break

if start_idx != -1:
    end_idx = -1
    open_brackets = 0
    for i in range(start_idx, len(lines)):
        open_brackets += lines[i].count('{') - lines[i].count('}')
        if open_brackets == 0 and i > start_idx:
            end_idx = i
            break
            
    # Remove old MediaCompareSlider
    content = "".join(lines[:start_idx])
    content_after = "".join(lines[end_idx+1:])
    
    # Add Camera import
    if "Camera" not in content and "Camera" not in content_after:
        content = re.sub(r'(import \{[^\}]*?)( \} from \'lucide-react\';)', r'\1, Camera\2', content)

    new_slider = """const MediaCompareSlider = ({ beforeSrc, afterSrc, isVideo }: { beforeSrc: string, afterSrc: string, isVideo: boolean }) => {
  const [position, setPosition] = useState(50);
  const [mobileView, setMobileView] = useState<'before' | 'after'>('after');
  const beforeRef = useRef<HTMLVideoElement>(null);
  const afterRef = useRef<HTMLVideoElement>(null);
  const mobileVideoRef = useRef<HTMLVideoElement>(null);

  const syncVideos = (action: 'play' | 'pause') => {
    if (!isVideo || !beforeRef.current || !afterRef.current) return;
    if (action === 'play') {
      beforeRef.current.play().catch(() => {});
      afterRef.current.play().catch(() => {});
    } else {
      beforeRef.current.pause();
      afterRef.current.pause();
    }
  };

  const handleExportFrame = () => {
    if (!isVideo) return;
    
    // Determine which video element to use (desktop or mobile)
    let sourceVideo: HTMLVideoElement | null = null;
    let isDesktop = window.innerWidth >= 768;
    
    if (isDesktop && afterRef.current) {
      sourceVideo = afterRef.current;
    } else if (!isDesktop && mobileVideoRef.current) {
      sourceVideo = mobileVideoRef.current;
    }
    
    if (!sourceVideo || sourceVideo.readyState < 2) return;
    
    try {
      const canvas = document.createElement('canvas');
      canvas.width = sourceVideo.videoWidth || 1920;
      canvas.height = sourceVideo.videoHeight || 1080;
      
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      
      ctx.drawImage(sourceVideo, 0, 0, canvas.width, canvas.height);
      
      canvas.toBlob((blob) => {
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const time = sourceVideo?.currentTime.toFixed(2) || '0.00';
        a.download = `neoFace_frame_${time}s.jpg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 'image/jpeg', 0.95);
    } catch (err) {
      console.error('Failed to export frame:', err);
      alert('Could not export frame. Ensure the video server sets CORS headers.');
    }
  };

  return (
    <div className="relative w-full aspect-video bg-black rounded-3xl overflow-hidden group border border-slate-200 mt-8 shadow-sm">
      
      {/* --- DESKTOP SLIDER VIEW (hidden on mobile) --- */}
      <div className="hidden md:block absolute inset-0 w-full h-full">
        {/* Before Media */}
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
        )}
        {/* After Media */}
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
        )}
        
        {/* Slider Handle */}
        <div 
          className="absolute top-0 bottom-0 w-1 bg-white cursor-ew-resize z-10 pointer-events-none"
          style={{ left: `${position}%` }}
        >
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full shadow-[0_0_15px_rgba(0,0,0,0.5)] flex items-center justify-center">
            <div className="w-1 h-4 bg-slate-400 rounded-full mx-0.5" />
            <div className="w-1 h-4 bg-slate-400 rounded-full mx-0.5" />
          </div>
        </div>
        
        <input 
          type="range"
          min={0}
          max={100}
          value={position}
          onChange={(e) => setPosition(Number(e.target.value))}
          className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-20"
        />
        
        <div className="absolute top-4 left-4 bg-black/60 text-white px-3 py-1 rounded-md text-sm font-medium backdrop-blur-sm pointer-events-none shadow-sm z-30">Original</div>
        <div className="absolute top-4 right-4 bg-black/60 text-white px-3 py-1 rounded-md text-sm font-medium backdrop-blur-sm pointer-events-none shadow-sm z-30">Processed</div>
      </div>

      {/* --- MOBILE TOGGLE VIEW (hidden on desktop) --- */}
      <div className="md:hidden absolute inset-0 w-full h-full flex flex-col">
        <div className="relative flex-1 w-full h-full">
          {isVideo ? (
            <video
              ref={mobileVideoRef}
              src={mobileView === 'before' ? beforeSrc : afterSrc}
              crossOrigin="anonymous"
              className="absolute inset-0 w-full h-full object-contain"
              muted
              loop
              controls
              autoPlay
              playsInline
            />
          ) : (
            // eslint-disable-next-line @next/next/no-img-element
            <img 
              src={mobileView === 'before' ? beforeSrc : afterSrc} 
              alt={mobileView === 'before' ? "Original" : "Processed"} 
              crossOrigin="anonymous"
              className="absolute inset-0 w-full h-full object-contain" 
            />
          )}
        </div>
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/70 backdrop-blur-md rounded-full p-1 flex gap-1 z-30 shadow-lg border border-white/20">
          <button 
            onClick={() => setMobileView('before')}
            className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-all ${mobileView === 'before' ? 'bg-white text-black' : 'text-white/70 hover:text-white'}`}
          >
            Original
          </button>
          <button 
            onClick={() => setMobileView('after')}
            className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-all ${mobileView === 'after' ? 'bg-white text-black' : 'text-white/70 hover:text-white'}`}
          >
            Processed
          </button>
        </div>
      </div>

      {/* Export Frame Button */}
      {isVideo && (
        <button
          onClick={handleExportFrame}
          className="absolute bottom-16 right-4 md:bottom-4 md:right-4 z-40 bg-indigo-600/90 hover:bg-indigo-500 text-white p-2.5 rounded-full shadow-lg backdrop-blur-md border border-white/20 transition-all flex items-center justify-center group/btn"
          title="Export current frame as image"
        >
          <Camera size={20} className="group-hover/btn:scale-110 transition-transform" />
        </button>
      )}

    </div>
  );
};
"""
    
    with open('app/page.tsx', 'w') as f:
        f.write(content + new_slider + content_after)
