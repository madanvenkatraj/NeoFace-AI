import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Loader2 } from 'lucide-react';
import ProgressBar from './ProgressBar';

interface ProcessingOverlayProps {
  isVisible: boolean;
  progress: number;
  statusMsg?: string;
  eta?: string;
  theme?: 'indigo' | 'cyan';
  onCancel?: () => void;
}

export default function ProcessingOverlay({ isVisible, progress, statusMsg, eta, theme = 'indigo', onCancel }: ProcessingOverlayProps) {
  const isCyan = theme === 'cyan';
  const overlayBg = isCyan ? 'bg-black/80' : 'bg-slate-900/60';
  const panelBg = isCyan ? 'bg-slate-900 border border-white/10' : 'bg-white border border-slate-200';
  const textColor = isCyan ? 'text-white' : 'text-slate-900';
  const loaderColor = isCyan ? 'text-cyan-400' : 'text-indigo-600';

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className={`fixed inset-0 z-[100] flex items-center justify-center p-4 backdrop-blur-md ${overlayBg}`}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={`w-full max-w-lg p-8 md:p-10 rounded-[2rem] shadow-2xl flex flex-col items-center text-center relative overflow-hidden ${panelBg}`}
          >
            {/* Ambient Background Glow */}
            <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full blur-[80px] opacity-20 pointer-events-none ${isCyan ? 'bg-cyan-500' : 'bg-indigo-600'}`} />

            <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full mb-6 relative ${isCyan ? 'bg-cyan-500/10 border border-cyan-500/20' : 'bg-indigo-50 border border-indigo-100'}`}>
              <Loader2 size={40} className={`${loaderColor} animate-spin`} />
              <div className={`absolute inset-0 rounded-full border animate-ping opacity-20 ${isCyan ? 'border-cyan-400' : 'border-indigo-500'}`} />
            </div>

            <h2 className={`text-2xl font-bold mb-2 relative z-10 ${textColor}`}>
              Processing Media
            </h2>
            <p className={`text-sm mb-10 relative z-10 ${isCyan ? 'text-slate-400' : 'text-slate-500'}`}>
              Please wait while the neural networks complete the operation. Do not close this window.
            </p>

            <div className="w-full relative z-10">
              <ProgressBar 
                progress={progress} 
                statusMsg={statusMsg || "Processing..."} 
                eta={eta}
                theme={theme} 
              />
            </div>
            
            {onCancel && (
              <button
                onClick={onCancel}
                className={`mt-8 px-6 py-2.5 rounded-xl text-sm font-semibold transition-colors relative z-10 ${
                  isCyan 
                    ? 'bg-white/10 hover:bg-white/20 text-white' 
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                }`}
              >
                Cancel Process
              </button>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
