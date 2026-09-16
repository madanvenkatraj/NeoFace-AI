import React from 'react';
import { Activity, Clock, Layers, Zap } from 'lucide-react';

interface ProcessingDiagnosticsProps {
  metrics: {
    process_time_s: number;
    frames: number;
    fps: number;
  };
}

export default function ProcessingDiagnostics({ metrics }: ProcessingDiagnosticsProps) {
  if (!metrics) return null;

  return (
    <div className="w-full mt-4 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-6 border-b border-slate-100 pb-3">
        <Activity className="text-indigo-600" size={20} />
        <h3 className="font-semibold text-slate-800">Processing Diagnostics</h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex items-start gap-4">
          <div className="p-3 bg-indigo-100 text-indigo-600 rounded-lg">
            <Clock size={24} />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Total Time</p>
            <p className="text-2xl font-bold text-slate-800">{metrics.process_time_s.toFixed(2)}<span className="text-sm font-medium text-slate-500 ml-1">sec</span></p>
          </div>
        </div>

        <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex items-start gap-4">
          <div className="p-3 bg-blue-100 text-blue-600 rounded-lg">
            <Layers size={24} />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Processed Frames</p>
            <p className="text-2xl font-bold text-slate-800">{metrics.frames}<span className="text-sm font-medium text-slate-500 ml-1">frames</span></p>
          </div>
        </div>

        <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex items-start gap-4">
          <div className="p-3 bg-emerald-100 text-emerald-600 rounded-lg">
            <Zap size={24} />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Average Speed</p>
            <p className="text-2xl font-bold text-slate-800">{metrics.fps.toFixed(2)}<span className="text-sm font-medium text-slate-500 ml-1">FPS</span></p>
          </div>
        </div>
      </div>
    </div>
  );
}
