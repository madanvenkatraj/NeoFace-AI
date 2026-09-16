'use client';
import { useState } from 'react';
import GeminiChat from './GeminiChat';
import { motion, AnimatePresence } from 'framer-motion';
import Image from 'next/image';

export default function GlobalChat() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            key="chat-button"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-4 right-4 z-50 w-14 h-14 rounded-full overflow-hidden shadow-lg border border-white/20 bg-black/50 backdrop-blur flex items-center justify-center cursor-pointer transition-colors hover:border-cyan-500/50 hover:shadow-[0_0_15px_rgba(6,182,212,0.4)]"
          >
            <motion.div 
              animate={{ 
                y: [0, -5, 0],
                scale: [1, 1.02, 1]
              }}
              transition={{
                duration: 3,
                ease: "easeInOut",
                repeat: Infinity,
              }}
              className="relative w-full h-full"
            >
              <Image 
                src="/NeoFace AI LOGO.png" 
                alt="NeoFace AI Chat" 
                fill
                className="object-cover scale-110"
              />
            </motion.div>
          </motion.button>
        )}
      </AnimatePresence>
      
      <AnimatePresence>
        {isOpen && (
          <motion.div
            key="chat-window"
            initial={{ x: '100%', opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: '100%', opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 bottom-0 z-50"
          >
            <GeminiChat onClose={() => setIsOpen(false)} />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
