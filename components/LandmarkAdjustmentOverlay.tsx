"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { X, RotateCw, Move, Maximize2, RotateCcw } from 'lucide-react';

interface LandmarkAdjustmentOverlayProps {
  faceId: string;
  modifiers: { scale: number; rotate: number; x: number; y: number };
  onChange: (modifiers: { scale: number; rotate: number; x: number; y: number }) => void;
  onClose: () => void;
}

export default function LandmarkAdjustmentOverlay({ faceId, modifiers, onChange, onClose }: LandmarkAdjustmentOverlayProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-slate-900/90 backdrop-blur-md p-4 rounded-2xl border border-white/20 shadow-2xl z-50 min-w-[300px]"
    >
      <div className="flex justify-between items-center mb-4 border-b border-white/10 pb-2">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Move size={14} className="text-indigo-400" /> Landmark Adjustments
        </h3>
        <button onClick={onClose} className="text-slate-400 hover:text-white">
          <X size={16} />
        </button>
      </div>

      <div className="flex flex-col gap-4">
        {/* Scale */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs text-slate-300">
            <span className="flex items-center gap-1"><Maximize2 size={12} /> Scale</span>
            <span>{modifiers.scale.toFixed(2)}x</span>
          </div>
          <input 
            type="range" 
            min="0.5" max="2" step="0.05" 
            value={modifiers.scale} 
            onChange={e => onChange({ ...modifiers, scale: parseFloat(e.target.value) })}
            className="w-full accent-indigo-500"
          />
        </div>

        {/* Rotate */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs text-slate-300">
            <span className="flex items-center gap-1"><RotateCw size={12} /> Rotation</span>
            <span>{modifiers.rotate}°</span>
          </div>
          <input 
            type="range" 
            min="-45" max="45" step="1" 
            value={modifiers.rotate} 
            onChange={e => onChange({ ...modifiers, rotate: parseFloat(e.target.value) })}
            className="w-full accent-indigo-500"
          />
        </div>

        {/* X Offset */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs text-slate-300">
            <span className="flex items-center gap-1">X Offset</span>
            <span>{modifiers.x}px</span>
          </div>
          <input 
            type="range" 
            min="-100" max="100" step="1" 
            value={modifiers.x} 
            onChange={e => onChange({ ...modifiers, x: parseFloat(e.target.value) })}
            className="w-full accent-indigo-500"
          />
        </div>

        {/* Y Offset */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs text-slate-300">
            <span className="flex items-center gap-1">Y Offset</span>
            <span>{modifiers.y}px</span>
          </div>
          <input 
            type="range" 
            min="-100" max="100" step="1" 
            value={modifiers.y} 
            onChange={e => onChange({ ...modifiers, y: parseFloat(e.target.value) })}
            className="w-full accent-indigo-500"
          />
        </div>

        <button 
          onClick={() => onChange({ scale: 1, rotate: 0, x: 0, y: 0 })}
          className="mt-2 text-xs text-indigo-400 hover:text-indigo-300 text-center flex items-center justify-center gap-1 font-semibold"
        >
          <RotateCcw size={12} /> Reset to Defaults
        </button>
      </div>
    </motion.div>
  );
}
