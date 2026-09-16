'use client';
import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, X, Mic, MicOff } from 'lucide-react';
import { useWorkspaceStore } from '../lib/store';
import { motion } from 'framer-motion';
import Image from 'next/image';

export default function GeminiChat({ onClose }: { onClose: () => void }) {
  const { undo, redo } = useWorkspaceStore();
  const [messages, setMessages] = useState<{role: 'user'|'assistant', content: string}[]>([
    { role: 'assistant', content: 'Hi! I am your NeoFace Studio Assistant. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!voiceEnabled) return;
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onresult = (event: any) => {
      const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
      if (transcript.includes('undo')) undo();
      else if (transcript.includes('redo')) redo();
      else setInput(prev => prev + (prev ? ' ' : '') + transcript);
    };

    recognition.start();
    return () => recognition.stop();
  }, [voiceEnabled, undo, redo]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    
    const newMsgs = [...messages, { role: 'user' as const, content: input }];
    setMessages(newMsgs);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMsgs })
      });
      const data = await res.json();
      
      if (res.ok) {
        setMessages([...newMsgs, { role: 'assistant', content: data.text }]);
      } else {
        setMessages([...newMsgs, { role: 'assistant', content: 'Sorry, I encountered an error.' }]);
      }
    } catch (e) {
      setMessages([...newMsgs, { role: 'assistant', content: 'Connection error.' }]);
    }
    setIsLoading(false);
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border-l border-white/10 shadow-2xl w-80">
      <div className="flex items-center justify-between p-4 border-b border-white/10 bg-black/20">
        <div className="flex items-center gap-3 text-cyan-400 font-bold">
          <motion.div
            animate={{ 
              y: [0, -3, 0],
              scale: [1, 1.05, 1]
            }}
            transition={{
              duration: 3,
              ease: "easeInOut",
              repeat: Infinity,
            }}
            className="relative w-8 h-8 rounded-full overflow-hidden bg-black border border-cyan-500/30 flex items-center justify-center shadow-[0_0_10px_rgba(6,182,212,0.3)]"
          >
            <Image 
              src="/NeoFace AI LOGO.png" 
              alt="NeoFace AI Logo" 
              fill
              className="object-cover"
            />
          </motion.div>
          <span>NeoFace Assistant</span>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-white">
          <X size={20} />
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 custom-scrollbar" ref={scrollRef}>
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 rounded-xl text-sm ${m.role === 'user' ? 'bg-cyan-600 text-white rounded-br-sm' : 'bg-white/10 text-slate-200 rounded-bl-sm'}`}>
              {m.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white/10 p-3 rounded-xl rounded-bl-sm flex gap-2 items-center text-cyan-400">
              <Loader2 size={16} className="animate-spin" />
              <span className="text-xs">Thinking...</span>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-white/10 bg-black/20">
        <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex gap-2 relative">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about settings, tools..."
            className="w-full bg-white/5 border border-white/10 rounded-lg pl-3 pr-16 py-2 text-sm text-white focus:outline-none focus:border-cyan-500 transition-colors"
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
            <button 
              type="button" 
              onClick={() => setVoiceEnabled(!voiceEnabled)} 
              className={`p-1.5 rounded-full transition-colors ${voiceEnabled ? 'text-emerald-400 bg-emerald-500/20' : 'text-slate-400 hover:text-white'}`}
            >
              {voiceEnabled ? <Mic size={14} /> : <MicOff size={14} />}
            </button>
            <button type="submit" disabled={!input.trim() || isLoading} className="p-1.5 text-cyan-500 disabled:text-slate-500 hover:text-cyan-400 transition-colors">
              <Send size={14} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
