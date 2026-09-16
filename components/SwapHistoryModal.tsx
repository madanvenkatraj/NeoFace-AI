'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { auth, db } from '../lib/firebase';
import { collection, query, orderBy, onSnapshot, doc, deleteDoc } from 'firebase/firestore';
import { X, Clock, Video, Image as ImageIcon, Trash2, Download, ExternalLink, History, Loader2 } from 'lucide-react';

interface SwapResult {
  id: string;
  resultUrl: string;
  isVideo: boolean;
  qualityMode?: string;
  facesSwapped?: number;
  createdAt: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SwapHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SwapHistoryModal({ isOpen, onClose }: SwapHistoryModalProps) {
  const [history, setHistory] = useState<SwapResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen || !auth.currentUser) return;
    
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    const q = query(
      collection(db, 'users', auth.currentUser.uid, 'swapHistory'),
      orderBy('createdAt', 'desc')
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const results = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      })) as SwapResult[];
      setHistory(results);
      setLoading(false);
    }, (error) => {
      console.error('Firestore Error: ', JSON.stringify({
        error: error.message,
        operationType: 'list',
        path: `users/${auth.currentUser?.uid}/swapHistory`,
        authInfo: { userId: auth.currentUser?.uid }
      }));
      setLoading(false);
    });

    return () => unsubscribe();
  }, [isOpen]);

  const handleDelete = async (id: string) => {
    if (!auth.currentUser) return;
    setDeletingId(id);
    try {
      await deleteDoc(doc(db, 'users', auth.currentUser.uid, 'swapHistory', id));
    } catch (error: any) {
      console.error('Firestore Error: ', JSON.stringify({
        error: error.message,
        operationType: 'delete',
        path: `users/${auth.currentUser.uid}/swapHistory/${id}`,
        authInfo: { userId: auth.currentUser.uid }
      }));
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          exit={{ opacity: 0 }} 
          className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
        >
          <motion.div 
            initial={{ scale: 0.95, opacity: 0, y: 20 }} 
            animate={{ scale: 1, opacity: 1, y: 0 }} 
            exit={{ scale: 0.95, opacity: 0, y: 20 }} 
            className="bg-slate-900 border border-white/10 p-6 md:p-8 rounded-[2rem] w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl relative overflow-hidden"
          >
            {/* Header */}
            <div className="flex justify-between items-center border-b border-white/10 pb-6 mb-6">
              <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                <History className="text-indigo-400" size={28} /> 
                Swap History
              </h2>
              <button onClick={onClose} className="w-10 h-10 flex items-center justify-center rounded-full bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 transition-colors">
                <X size={20} />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
              {!auth.currentUser ? (
                <div className="text-center py-20">
                  <p className="text-slate-400">Please sign in to view your history.</p>
                </div>
              ) : loading ? (
                <div className="flex justify-center items-center py-20">
                  <Loader2 className="animate-spin text-indigo-500" size={32} />
                </div>
              ) : history.length === 0 ? (
                <div className="text-center py-20 flex flex-col items-center justify-center">
                  <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mb-4">
                    <History className="text-slate-500" size={32} />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">No History Found</h3>
                  <p className="text-slate-400 max-w-sm">You haven&apos;t generated any face swaps yet. Your results will automatically appear here once a job completes.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {history.map((item) => (
                    <div key={item.id} className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden group hover:border-white/20 transition-all flex flex-col">
                      <div className="aspect-video bg-black relative flex items-center justify-center">
                        {item.isVideo ? (
                          <Video className="text-slate-600 absolute" size={32} />
                        ) : (
                          <ImageIcon className="text-slate-600 absolute" size={32} />
                        )}
                        <img 
                          src={item.resultUrl.startsWith('http') ? item.resultUrl : `${API_URL}/outputs/${item.resultUrl.split('/').pop()}`}
                          alt="Swap Result" 
                          className="w-full h-full object-contain relative z-10"
                          onError={(e) => {
                            // Hide image if broken (e.g. video file or purged from local disk)
                            (e.target as HTMLImageElement).style.opacity = '0';
                          }}
                        />
                        <div className="absolute top-3 left-3 z-20 flex gap-2">
                          <span className="px-2 py-1 bg-black/60 backdrop-blur-md rounded-md text-[10px] font-bold text-white uppercase tracking-wider border border-white/10 flex items-center gap-1">
                            {item.isVideo ? <Video size={10} /> : <ImageIcon size={10} />}
                            {item.isVideo ? 'Video' : 'Image'}
                          </span>
                          {item.qualityMode && (
                            <span className="px-2 py-1 bg-indigo-500/20 backdrop-blur-md rounded-md text-[10px] font-bold text-indigo-300 uppercase tracking-wider border border-indigo-500/30">
                              {item.qualityMode}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="p-4 flex flex-col gap-3 flex-1">
                        <div className="flex justify-between items-start">
                          <div className="flex flex-col">
                            <span className="text-xs text-slate-400 flex items-center gap-1">
                              <Clock size={12} />
                              {new Date(item.createdAt).toLocaleString()}
                            </span>
                            {item.facesSwapped !== undefined && (
                              <span className="text-xs text-slate-500 mt-1">
                                {item.facesSwapped} {item.facesSwapped === 1 ? 'face' : 'faces'} swapped
                              </span>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex gap-2 mt-auto pt-2">
                          <a 
                            href={item.resultUrl.startsWith('http') ? item.resultUrl : `${API_URL}/outputs/${item.resultUrl.split('/').pop()}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1 bg-white/10 hover:bg-white/20 text-white py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
                          >
                            <ExternalLink size={14} /> Open
                          </a>
                          <a 
                            href={item.resultUrl.startsWith('http') ? item.resultUrl : `${API_URL}/outputs/${item.resultUrl.split('/').pop()}`}
                            download={`neoface_result_${item.id}.${item.isVideo ? 'mp4' : 'jpg'}`}
                            className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
                          >
                            <Download size={14} /> Download
                          </a>
                          <button 
                            onClick={() => handleDelete(item.id)}
                            disabled={deletingId === item.id}
                            className="w-10 h-10 shrink-0 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg flex items-center justify-center transition-colors disabled:opacity-50"
                          >
                            {deletingId === item.id ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
