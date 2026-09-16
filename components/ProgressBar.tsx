import { motion } from 'motion/react';

interface ProgressBarProps {
  progress: number;
  statusMsg?: string;
  eta?: string;
  className?: string;
  theme?: 'indigo' | 'cyan';
}

export default function ProgressBar({ progress, statusMsg, eta, className = '', theme = 'indigo' }: ProgressBarProps) {
  const isCyan = theme === 'cyan';
  const bgColor = isCyan ? 'bg-cyan-500' : 'bg-indigo-600';
  const textColor = isCyan ? 'text-cyan-400' : 'text-indigo-600';
  const shadowColor = isCyan ? 'shadow-[0_0_15px_rgba(6,182,212,0.6)]' : 'shadow-[0_0_10px_rgba(79,70,229,0.5)]';

  return (
    <div className={`w-full flex flex-col gap-2 ${className}`}>
      <div className="flex justify-between items-end text-sm">
        <span className={`font-semibold ${isCyan ? 'text-white' : 'text-slate-700 dark:text-slate-300'}`}>
          {statusMsg || "Processing..."}
        </span>
        <div className="flex flex-col items-end">
          <span className={`${textColor} font-bold`}>{Math.round(progress)}%</span>
          {eta && <span className={`text-xs font-mono mt-1 ${isCyan ? 'text-slate-400' : 'text-slate-500'}`}>ETA: {eta}</span>}
        </div>
      </div>
      <div className={`w-full ${isCyan ? 'bg-white/10' : 'bg-slate-200 dark:bg-slate-800'} rounded-full h-3 overflow-hidden relative`}>
        <motion.div 
          className={`${bgColor} h-3 rounded-full ${shadowColor}`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ ease: "easeOut", duration: 0.3 }}
        />
        {/* Animated shimmer effect */}
        {progress > 0 && progress < 100 && (
          <motion.div 
            className="absolute top-0 bottom-0 w-1/2 bg-gradient-to-r from-transparent via-white/30 to-transparent"
            initial={{ x: '-200%' }}
            animate={{ x: '200%' }}
            transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
          />
        )}
      </div>
    </div>
  );
}
