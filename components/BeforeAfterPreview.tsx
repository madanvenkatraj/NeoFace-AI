import React, { useState, useRef, useEffect } from 'react';
import { Download } from 'lucide-react';

interface BeforeAfterPreviewProps {
  originalSrc: string;
  resultSrc: string;
  isVideo: boolean;
  downloadName?: string;
}

export default function BeforeAfterPreview({ originalSrc, resultSrc, isVideo, downloadName = 'result' }: BeforeAfterPreviewProps) {
  const [sliderPos, setSliderPos] = useState(50);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Video sync references
  const origVideoRef = useRef<HTMLVideoElement>(null);
  const resultVideoRef = useRef<HTMLVideoElement>(null);

  // Sync videos if applicable
  useEffect(() => {
    if (!isVideo || !origVideoRef.current || !resultVideoRef.current) return;
    
    const orig = origVideoRef.current;
    const res = resultVideoRef.current;
    
    const handlePlay = () => res.play().catch(() => {});
    const handlePause = () => res.pause();
    const handleSeek = () => { res.currentTime = orig.currentTime; };
    const handleWaiting = () => res.pause();
    const handlePlaying = () => res.play().catch(() => {});

    orig.addEventListener('play', handlePlay);
    orig.addEventListener('pause', handlePause);
    orig.addEventListener('seeked', handleSeek);
    orig.addEventListener('waiting', handleWaiting);
    orig.addEventListener('playing', handlePlaying);
    
    // Ensure muted for result to prevent echo
    res.muted = true;

    return () => {
      orig.removeEventListener('play', handlePlay);
      orig.removeEventListener('pause', handlePause);
      orig.removeEventListener('seeked', handleSeek);
      orig.removeEventListener('waiting', handleWaiting);
      orig.removeEventListener('playing', handlePlaying);
    };
  }, [isVideo]);

  const handleMouseMove = (e: React.MouseEvent | React.TouchEvent) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    
    let clientX = 0;
    if ('touches' in e) {
      clientX = e.touches[0].clientX;
    } else {
      // Button must be pressed for drag, but let's just make it hover-based or drag-based.
      // Hover-based is smoother for this component.
      clientX = (e as React.MouseEvent).clientX;
    }

    const pos = Math.max(0, Math.min(100, ((clientX - rect.left) / rect.width) * 100));
    setSliderPos(pos);
  };

  return (
    <div className="flex flex-col gap-4 w-full">
      <div 
        ref={containerRef}
        className="relative w-full aspect-video bg-black rounded-2xl overflow-hidden select-none group cursor-ew-resize"
        onMouseMove={handleMouseMove}
        onTouchMove={handleMouseMove}
      >
        {/* ORIGINAL (Bottom Layer) */}
        <div className="absolute inset-0 flex items-center justify-center">
          {isVideo ? (
            <video 
              ref={origVideoRef}
              src={originalSrc} 
              className="w-full h-full object-contain pointer-events-auto" 
              controls
              crossOrigin="anonymous"
              controlsList="nodownload noplaybackrate"
            />
          ) : (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img src={originalSrc} alt="Original" className="w-full h-full object-contain pointer-events-none" />
          )}
        </div>
        
        <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded text-xs font-bold text-white/70 tracking-widest uppercase border border-white/10 z-10 pointer-events-none">Original</div>

        {/* PROCESSED (Top Layer clipped) */}
        <div 
          className="absolute inset-0 flex items-center justify-center pointer-events-none"
          style={{ clipPath: `inset(0 ${100 - sliderPos}% 0 0)` }}
        >
          {isVideo ? (
            <video 
              ref={resultVideoRef}
              src={resultSrc} 
              className="w-full h-full object-contain pointer-events-none" 
              crossOrigin="anonymous"
            />
          ) : (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img src={resultSrc} alt="Result" className="w-full h-full object-contain pointer-events-none" />
          )}
        </div>
        
        <div className="absolute top-4 right-4 bg-emerald-500/20 backdrop-blur-md px-3 py-1.5 rounded text-xs font-bold text-emerald-400 tracking-widest uppercase border border-emerald-500/30 z-10 pointer-events-none">Processed</div>

        {/* SLIDER LINE */}
        <div 
          className="absolute top-0 bottom-0 w-0.5 bg-white shadow-[0_0_10px_rgba(0,0,0,0.5)] z-20 pointer-events-none"
          style={{ left: `${sliderPos}%` }}
        >
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center">
            <div className="flex gap-1">
              <div className="w-0.5 h-3 bg-slate-300 rounded-full"></div>
              <div className="w-0.5 h-3 bg-slate-300 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="flex justify-end">
        <a 
          href={resultSrc}
          download={downloadName}
          className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold shadow-sm transition-all whitespace-nowrap flex items-center gap-2"
        >
          <Download size={18} /> Download Result
        </a>
      </div>
    </div>
  );
}
