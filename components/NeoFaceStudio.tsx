'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  UploadCloud, 
  Image as ImageIcon, 
  Video, 
  Play, 
  Loader2, 
  CheckCircle2, 
  Download, 
  ArrowRight,
  RefreshCw,
  Camera,
  Layers,
  ChevronRight,
  Settings2,
  X,
  PlayCircle,
  Pause,
  Scissors,
  Wand2,
  Clock,
  Film,
  Archive,
  ListOrdered,
  Plus,
  Palette,
  Brush,
  SlidersHorizontal,
  Save,
  Keyboard,
  Focus,
  FolderHeart,
  MonitorPlay,
  Bell,
  BellOff,
  RotateCcw,
  Filter,
  Activity,
  Cpu,
  BrainCircuit,
  Eye,
  GripHorizontal,
  SaveAll,
  Zap,
  Flame,
  Trash2
} from 'lucide-react';
import Image from 'next/image';
import AuthButton from './AuthButton';
import SwapHistoryModal from './SwapHistoryModal';
import { History } from 'lucide-react';
import CloudSyncButton from './CloudSyncButton';
import DrivePicker from './DrivePicker';
import { useWorkspaceStore } from '../lib/store';
import ProgressBar from './ProgressBar';

// MOCK DATA

const MOCK_HISTORY = [
  { id: 'h1', date: '2 mins ago', faces: 2, status: 'Completed', targetSrc: 'https://picsum.photos/seed/hist1/100/100' },
  { id: 'h2', date: '1 hour ago', faces: 1, status: 'Completed', targetSrc: 'https://picsum.photos/seed/hist2/100/100' },
];

const MOCK_TARGET_FACES = [
  { id: 't1', url: 'https://picsum.photos/seed/face1/200/200', label: 'Person 1' },
  { id: 't2', url: 'https://picsum.photos/seed/face2/200/200', label: 'Person 2' },
];

const MOCK_SOURCE_FACES = [
  { id: 's1', url: 'https://picsum.photos/seed/source1/200/200', label: 'Source A' },
];

export default function NeoFaceStudio() {
  const { present, past, future, setSetting, undo, redo } = useWorkspaceStore();

  const [currentStep, setCurrentStep] = useState<1 | 2 | 3 | 4 | 5>(1);
  const [targetMedia, setTargetMedia] = useState<File | null>(null);
  const [targetPreview, setTargetPreview] = useState<string | null>(null);
  
  // Step 2 & 3 State
  const [selectedTargetId, setSelectedTargetId] = useState<string | null>(null);
  const [mappedFaces, setMappedFaces] = useState<Record<string, string | 'skip'>>({});
  const [refinerEnabled, setRefinerEnabled] = useState(true);
  
  // Step 4 State
  const [progress, setProgress] = useState(0);
  const [currentProcessStep, setCurrentProcessStep] = useState(0);
  
  // Step 5 State
  const [sliderPos, setSliderPos] = useState(50);
  const [sceneMarkers, setSceneMarkers] = useState<number[]>([]);
  const [isDetectingScenes, setIsDetectingScenes] = useState(false);
  const [timelinePos, setTimelinePos] = useState(0);
  
  // History & Export States
  const [showHistory, setShowHistory] = useState(false);
  const [showExportPreview, setShowExportPreview] = useState(false);

  // Post-processing
  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);
  const [temperature, setTemperature] = useState(0);

  // Batch Queue
  const [showBatchQueue, setShowBatchQueue] = useState(false);
  const [smartPrioritization, setSmartPrioritization] = useState(false);
  const [showMaskOverlay, setShowMaskOverlay] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(false);


  const [batchJobs, setBatchJobs] = useState([
    { id: 'b1', name: 'Scene_01_Interview.mp4', status: 'Processing', progress: 45 }, 
    { id: 'b2', name: 'Scene_02_B-Roll.mp4', status: 'Queued', progress: 0 }
  ]);

    
  // New Extra Features
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const [autoOrient, setAutoOrient] = useState(true);
  const [genderFilter, setGenderFilter] = useState('All');
  

  // Advanced AI Features
  const [occlusionDetection, setOcclusionDetection] = useState(true);
  const [microExpressions, setMicroExpressions] = useState(false);
  const [trimRange, setTrimRange] = useState<[number, number]>([0, 100]); // 0-100% of video
  
  // VRAM Diagnostics
  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const [vramUsage, setVramUsage] = useState(6.4); // Mock GB
  const [vramMax, setVramMax] = useState(12.0); // Mock GB
  
  // Custom Masks
  const [savedMasks, setSavedMasks] = useState<{id: string, name: string}[]>([]);

  // Extend Batch Jobs
  const [batchJobsEx, setBatchJobsEx] = useState([
    { id: 'b1', name: 'Scene_01_Interview.mp4', status: 'Processing', progress: 45, eta: '2m 14s', gpu: '85% VRAM' }, 
    { id: 'b2', name: 'Scene_02_B-Roll.mp4', status: 'Queued', progress: 0, eta: 'Pending', gpu: '-' }
  ]);

  // Tab Sync (Processing History)
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'neoface_batch_jobs' && e.newValue) {
        try {
          setBatchJobsEx(JSON.parse(e.newValue));
        } catch(err) {}
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => {
    localStorage.setItem('neoface_batch_jobs', JSON.stringify(batchJobsEx));
  }, [batchJobsEx]);

  // Load workspace state from localStorage on mount
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => {
    const savedState = localStorage.getItem('neoface_ui_state');
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        if (parsed.refinerEnabled !== undefined) // eslint-disable-next-line react-hooks/set-state-in-effect
          setRefinerEnabled(parsed.refinerEnabled);
        if (parsed.brightness !== undefined) setBrightness(parsed.brightness);
        if (parsed.contrast !== undefined) setContrast(parsed.contrast);
        if (parsed.temperature !== undefined) setTemperature(parsed.temperature);
        if (parsed.autoOrient !== undefined) setAutoOrient(parsed.autoOrient);
        if (parsed.genderFilter !== undefined) setGenderFilter(parsed.genderFilter);
        if (parsed.occlusionDetection !== undefined) setOcclusionDetection(parsed.occlusionDetection);
        if (parsed.microExpressions !== undefined) setMicroExpressions(parsed.microExpressions);
        if (parsed.smartPrioritization !== undefined) setSmartPrioritization(parsed.smartPrioritization);
        if (parsed.showMaskOverlay !== undefined) setShowMaskOverlay(parsed.showMaskOverlay);
        if (parsed.showHeatmap !== undefined) setShowHeatmap(parsed.showHeatmap);
        if (parsed.notificationsEnabled !== undefined) setNotificationsEnabled(parsed.notificationsEnabled);
      } catch (e) {
        console.error('Failed to load NeoFace AI UI state', e);
      }
    }
  }, []);

  // Save workspace state to localStorage on change
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => {
    const stateToSave = {
      refinerEnabled,
      brightness,
      contrast,
      temperature,
      autoOrient,
      genderFilter,
      occlusionDetection,
      microExpressions,
      smartPrioritization,
      showMaskOverlay,
      showHeatmap,
      notificationsEnabled
    };
    localStorage.setItem('neoface_ui_state', JSON.stringify(stateToSave));
  }, [
    refinerEnabled, brightness, contrast, temperature, autoOrient, genderFilter, 
    occlusionDetection, microExpressions, smartPrioritization, showMaskOverlay, showHeatmap, notificationsEnabled
  ]);

  // Masking Tool
  const [isMasking, setIsMasking] = useState(false);
  const [isDrawing, setIsDrawing] = useState(false);
  const [maskPoints, setMaskPoints] = useState<{x: number, y: number}[]>([]);

  // New Features
  const [showExportSettings, setShowExportSettings] = useState(false);
  const [exportPreset, setExportPreset] = useState('1080p60');
  const [showLandmarks, setShowLandmarks] = useState(false);
  const [showGallery, setShowGallery] = useState(false);
  const [activeTargetForGallery, setActiveTargetForGallery] = useState<string | null>(null);
  const [savedSources, setSavedSources] = useState([
    {id: 's1', url: 'https://picsum.photos/seed/source1/200/200', label: 'Source A', gender: 'Female', confidence: 0.98},
    {id: 's2', url: 'https://picsum.photos/seed/source2/200/200', label: 'Saved B', gender: 'Male', confidence: 0.95},
    {id: 's3', url: 'https://picsum.photos/seed/source4/200/200', label: 'Low Qual C', gender: 'Female', confidence: 0.65},
    {id: 's4', url: 'https://picsum.photos/seed/source4/200/200', label: 'Duplicate C', gender: 'Female', confidence: 0.92}
  ]);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [isPlaying, setIsPlaying] = useState(true);


  const handleSceneDetect = () => {
    setIsDetectingScenes(true);
    // Simulate CV scene cut detection pipeline
    setTimeout(() => {
      setSceneMarkers([25, 45, 78]); // Percentage points where scenes change
      setIsDetectingScenes(false);
    }, 2000);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setTargetMedia(file);
      setTargetPreview(URL.createObjectURL(file));
      // Simulate auto-detect
      setTimeout(() => setCurrentStep(2), 1500);
    }
  };

  const handleStartProcessing = () => {
    setCurrentStep(4);
    setProgress(0);
    
    // Simulate process
    let currentP = 0;
    const interval = setInterval(() => {
      currentP += 2;
      setProgress(currentP);
      if (currentP < 20) setCurrentProcessStep(0);
      else if (currentP < 40) setCurrentProcessStep(1);
      else if (currentP < 70) setCurrentProcessStep(2);
      else if (currentP < 90) setCurrentProcessStep(3);
      else setCurrentProcessStep(4);
      
      if (currentP >= 100) {
        clearInterval(interval);
        setTimeout(() => setCurrentStep(5), 600);
      }
    }, 100);
  };

  const processSteps = [
    "Frame Extraction",
    "Face Alignment",
    "Inswapper Engine",
    refinerEnabled ? "CodeFormer Super-Resolution" : "Standard Blending",
    "Audio Remux"
  ];

  // Global Keyboard Shortcuts
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger shortcuts if user is typing in an input or textarea
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      // Undo: Ctrl+Z or Cmd+Z
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
        e.preventDefault();
        undo();
        return;
      }

      // Swap: 's' or 'S'
      if (e.key.toLowerCase() === 's') {
        if (currentStep === 3 && Object.keys(mappedFaces).length > 0) {
          e.preventDefault();
          handleStartProcessing();
        }
        return;
      }

      // Toggle Slider: Space
      if (e.code === 'Space') {
        if (currentStep === 5) {
          e.preventDefault();
          setSliderPos(prev => prev === 100 ? 0 : 100);
        }
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentStep, mappedFaces, undo]);

  return (
    <div className="w-full max-w-6xl mx-auto p-4 md:p-6 lg:p-8 flex flex-col gap-8 min-h-[85vh]">
      
      {/* Header & Stepper */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-4 relative z-20">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-br from-white to-slate-400 bg-clip-text text-transparent mb-1">
              NeoFace AI
            </h1>
            <p className="text-sm text-slate-400 font-medium">Professional Face Mapping Studio</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowHistory(true)}
              className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg text-sm font-semibold transition-colors flex items-center gap-2 border border-white/10"
            >
              <History size={16} className="text-indigo-400" />
              History
            </button>
            <CloudSyncButton />
            <AuthButton />
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 md:gap-3 overflow-x-auto hide-scrollbar pb-2 md:pb-0">
          {[1, 2, 3, 4, 5].map((step) => (
            <React.Fragment key={step}>
              <div 
                className={`flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold transition-all duration-300 shrink-0 ${
                  currentStep === step 
                    ? 'bg-cyan-500 text-white shadow-[0_0_15px_rgba(6,182,212,0.5)]' 
                    : currentStep > step 
                      ? 'bg-white/10 text-slate-300' 
                      : 'bg-white/[0.02] text-slate-600 border border-white/5'
                }`}
              >
                {currentStep > step ? <CheckCircle2 size={14} /> : step}
              </div>
              {step < 5 && (
                <div className={`w-8 h-px shrink-0 transition-colors duration-300 ${currentStep > step ? 'bg-cyan-500/50' : 'bg-white/10'}`} />
              )}
            </React.Fragment>
          ))}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 relative z-10 flex flex-col">
        <AnimatePresence mode="wait">
          
          {/* STEP 1: UPLOAD */}
          {currentStep === 1 && (
            <motion.div 
              key="step1"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="flex-1 flex flex-col items-center justify-center"
            >
              <div className="w-full max-w-3xl glass-panel rounded-3xl p-8 md:p-12 text-center border border-white/10 hover:border-cyan-500/30 transition-colors duration-500 group relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent pointer-events-none" />
                
                <input 
                  type="file" 
                  id="media-upload" 
                  className="hidden" 
                  accept="video/*,image/*"
                  onChange={handleFileUpload}
                />
                <div 
                  className="flex flex-col items-center justify-center gap-6 relative z-10"
                >
                  <label htmlFor="media-upload" className="cursor-pointer w-24 h-24 rounded-full bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 hover:scale-110 hover:bg-cyan-500/20 transition-all duration-500">
                    <UploadCloud size={40} strokeWidth={1.5} />
                  </label>
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Ingest Target Media</h3>
                    <p className="text-slate-400 text-sm max-w-md mx-auto leading-relaxed">
                      Drag and drop your high-resolution video or photo here, or click to browse. Supports up to 1GB MP4, MOV, JPG, PNG.
                    </p>
                  </div>
                  <div className="flex flex-col sm:flex-row items-center gap-4">
                    <label 
                      htmlFor="media-upload"
                      className="cursor-pointer px-6 py-2.5 rounded-full bg-white/5 border border-white/10 text-sm font-medium text-slate-200 hover:bg-white/10 transition-colors"
                    >
                      Select File
                    </label>
                    <DrivePicker 
                      onFilePicked={(file) => {
                        setTargetPreview(file.url);
                        setCurrentStep(2);
                      }}
                      className="px-6 py-2.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-sm font-medium text-cyan-400 hover:bg-cyan-500/20"
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* STEP 2 & 3: ROSTER AND MAPPING (COMBINED FOR FLUID UX) */}
          {(currentStep === 2 || currentStep === 3) && (
            <motion.div
              key="step23"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="flex flex-col lg:flex-row gap-6 lg:gap-8 flex-1"
            >
              {/* Left Column: Target Media Preview & Roster */}
              <div className="w-full lg:w-1/3 flex flex-col gap-6">
                <div className="glass-panel rounded-2xl overflow-hidden flex flex-col">
                  <div className="p-4 border-b border-white/5 bg-white/[0.02] flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                      <ImageIcon size={16} className="text-cyan-400" /> 
                      Target Media
                    </h3>
                    <span className="text-[10px] uppercase tracking-wider font-bold bg-white/10 text-slate-300 px-2 py-1 rounded-md">1920x1080</span>
                  </div>
                  <div className="relative aspect-video bg-black/50 overflow-hidden flex items-center justify-center">
                    {targetPreview ? (
                      <>
                        <Image src={targetPreview} alt="Preview" fill referrerPolicy="no-referrer" className="object-cover opacity-70" />
                        {showLandmarks && (
                          <div className="absolute inset-0 pointer-events-none">
                            {/* High-Fidelity Landmark Overlay */}
                            <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                              {/* Scanning Beam */}
                              <motion.rect x="0" y="0" width="100" height="2" fill="url(#cyan-beam)"
                                animate={{ y: [0, 100, 0] }}
                                transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                              />
                              <defs>
                                <linearGradient id="cyan-beam" x1="0%" y1="0%" x2="100%" y2="0%">
                                  <stop offset="0%" stopColor="transparent" />
                                  <stop offset="50%" stopColor="rgba(6,182,212,0.8)" />
                                  <stop offset="100%" stopColor="transparent" />
                                </linearGradient>
                              </defs>

                              {/* Face 1 Landmarks */}
                              <g transform="translate(45, 35) scale(0.15)">
                                {/* Jawline */}
                                <polyline points="-30,20 -20,40 0,50 20,40 30,20" fill="none" stroke="rgba(52,211,153,0.5)" strokeWidth="2" strokeDasharray="2,2"/>
                                {/* Eyes */}
                                <circle cx="-15" cy="-5" r="3" fill="#34d399" className="shadow-[0_0_8px_#34d399]" />
                                <circle cx="15" cy="-5" r="3" fill="#34d399" className="shadow-[0_0_8px_#34d399]" />
                                <polyline points="-20,-5 -10,-5" fill="none" stroke="#34d399" strokeWidth="1" />
                                <polyline points="10,-5 20,-5" fill="none" stroke="#34d399" strokeWidth="1" />
                                {/* Nose */}
                                <polyline points="0,-5 0,15 -5,20 5,20 0,15" fill="none" stroke="rgba(52,211,153,0.8)" strokeWidth="1.5" />
                                <circle cx="0" cy="18" r="2" fill="#34d399" />
                                {/* Mouth */}
                                <polyline points="-10,30 0,32 10,30 0,35 -10,30" fill="none" stroke="rgba(52,211,153,0.8)" strokeWidth="1.5" />
                                <circle cx="-10" cy="30" r="1.5" fill="#34d399" />
                                <circle cx="10" cy="30" r="1.5" fill="#34d399" />
                                <circle cx="0" cy="32" r="1.5" fill="#34d399" />
                                <circle cx="0" cy="35" r="1.5" fill="#34d399" />
                              </g>
                            </svg>
                            
                            <div className="absolute top-4 left-4 bg-black/50 backdrop-blur border border-emerald-500/30 text-emerald-400 px-2 py-1 rounded text-[10px] font-bold uppercase flex items-center gap-1">
                              <Focus size={12} /> Landmark Detection Active
                            </div>
                          </div>
                        )}
                      </>
                    ) : (
                      <Video size={48} className="text-white/10" />
                    )}
                  </div>
                  {targetPreview && targetMedia?.type.startsWith('video/') && (
                    <div className="p-3 border-t border-white/5 bg-black/40 flex flex-col gap-2">
                      <div className="flex justify-between items-center text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                        <span>Video Trimming</span>
                        <span className="text-cyan-400">{Math.round(trimRange[0])}% - {Math.round(trimRange[1])}%</span>
                      </div>
                      <div className="relative h-6 bg-white/5 rounded-md flex items-center px-2">
                        {/* Mock dual-thumb slider */}
                        <div className="absolute top-1 bottom-1 bg-cyan-500/30 rounded-sm" style={{ left: `${trimRange[0]}%`, right: `${100 - trimRange[1]}%` }}></div>
                        
                        <div 
                           className="absolute w-2 h-4 bg-white rounded cursor-ew-resize hover:scale-125 transition-transform z-10 shadow-md"
                           style={{ left: `calc(${trimRange[0]}% - 4px)` }}
                           onMouseDown={(e) => {
                             const parent = e.currentTarget.parentElement;
                             if (!parent) return;
                             const handleMove = (moveEvent: MouseEvent) => {
                               const rect = parent.getBoundingClientRect();
                               let newPos = ((moveEvent.clientX - rect.left) / rect.width) * 100;
                               newPos = Math.max(0, Math.min(newPos, trimRange[1] - 5));
                               setTrimRange([newPos, trimRange[1]]);
                             };
                             const handleUp = () => {
                               document.removeEventListener('mousemove', handleMove);
                               document.removeEventListener('mouseup', handleUp);
                             };
                             document.addEventListener('mousemove', handleMove);
                             document.addEventListener('mouseup', handleUp);
                           }}
                        />
                        <div 
                           className="absolute w-2 h-4 bg-white rounded cursor-ew-resize hover:scale-125 transition-transform z-10 shadow-md"
                           style={{ right: `calc(${100 - trimRange[1]}% - 4px)` }}
                           onMouseDown={(e) => {
                             const parent = e.currentTarget.parentElement;
                             if (!parent) return;
                             const handleMove = (moveEvent: MouseEvent) => {
                               const rect = parent.getBoundingClientRect();
                               let newPos = ((moveEvent.clientX - rect.left) / rect.width) * 100;
                               newPos = Math.max(trimRange[0] + 5, Math.min(newPos, 100));
                               setTrimRange([trimRange[0], newPos]);
                             };
                             const handleUp = () => {
                               document.removeEventListener('mousemove', handleMove);
                               document.removeEventListener('mouseup', handleUp);
                             };
                             document.addEventListener('mousemove', handleMove);
                             document.addEventListener('mouseup', handleUp);
                           }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                <div className="glass-panel rounded-2xl p-5 flex flex-col gap-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                      <Camera size={16} className="text-violet-400" />
                      Detected Faces ({MOCK_TARGET_FACES.length})
                    </h3>
                    <button 
                      onClick={() => setShowLandmarks(!showLandmarks)}
                      className={`px-2 py-1 rounded border text-xs font-bold transition-colors flex items-center gap-1 ${
                        showLandmarks ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-white/5 text-slate-400 border-white/10 hover:text-white'
                      }`}
                    >
                      <Focus size={12} /> {showLandmarks ? 'Hide Landmarks' : 'Show Landmarks'}
                    </button>
                  </div>
                  <div className="flex overflow-x-auto gap-3 pb-2 hide-scrollbar">
                    {MOCK_TARGET_FACES.map((face) => (
                      <button 
                        key={face.id}
                        onClick={() => setSelectedTargetId(face.id)}
                        className={`relative w-16 h-16 rounded-full overflow-hidden shrink-0 border-2 transition-all duration-300 ${
                          selectedTargetId === face.id ? 'border-cyan-400 scale-105 shadow-[0_0_15px_rgba(6,182,212,0.4)]' : 'border-white/10 hover:border-white/30 opacity-70 hover:opacity-100'
                        }`}
                      >
                        <Image src={face.url} alt={face.label} fill referrerPolicy="no-referrer" className="object-cover" />
                        {mappedFaces[face.id] && (
                          <div className="absolute inset-0 bg-emerald-500/20 backdrop-blur-[2px] flex items-center justify-center">
                            <CheckCircle2 size={24} className="text-emerald-400" />
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                  {currentStep === 2 && (
                    <button 
                      onClick={() => setCurrentStep(3)}
                      className="w-full py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-semibold transition-colors mt-2 shadow-lg shadow-cyan-900/20"
                    >
                      Continue to Mapping
                    </button>
                  )}
                </div>
              </div>

              {/* Right Column: Mapping Matrix */}
              <div className="w-full lg:w-2/3 glass-panel rounded-2xl flex flex-col h-full min-h-[400px]">
                <div className="p-5 border-b border-white/5 bg-white/[0.02] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                      <Layers size={16} className="text-emerald-400" />
                      Mapping Matrix
                    </h3>
                    
                    {/* Face Refiner Toggle */}
                    <div 
                      className="flex items-center gap-2 pl-4 ml-4 border-l border-white/10"
                      title="Apply super-resolution upscaling to the swapped faces for better detail preservation"
                    >
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Face Refiner</span>
                      <button
                        onClick={() => setRefinerEnabled(!refinerEnabled)}
                        className={`w-8 h-4 rounded-full transition-colors relative flex items-center ${refinerEnabled ? 'bg-cyan-500' : 'bg-white/10'}`}
                      >
                        <div className={`w-3 h-3 rounded-full bg-white absolute transition-transform duration-200 ${refinerEnabled ? 'translate-x-4' : 'translate-x-0.5'}`} />
                      </button>
                    </div>
                  </div>

                  {currentStep === 3 && Object.keys(mappedFaces).length === MOCK_TARGET_FACES.length && (
                    <div className="flex items-center gap-3">
                      <button 
                        onClick={() => {
                          setBatchJobs(prev => [...prev, { id: 'b' + Date.now(), name: 'New_Pipeline_Job.mp4', status: 'Queued', progress: 0 }]);
                          setShowBatchQueue(true);
                        }}
                        className="bg-white/10 text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-white/20 border border-white/10 transition-colors flex items-center gap-1.5"
                      >
                        <Plus size={12} /> Add to Queue
                      </button>
                      <button 
                        onClick={handleStartProcessing}
                        className="bg-white text-black px-4 py-1.5 rounded-lg text-xs font-bold hover:bg-slate-200 transition-colors flex items-center gap-1.5 shadow-[0_0_15px_rgba(255,255,255,0.2)]"
                      >
                        Process <Play size={12} fill="currentColor" />
                      </button>
                    </div>
                  )}
                </div>

                {currentStep === 2 ? (
                  <div className="flex-1 flex flex-col items-center justify-center text-center p-8 opacity-50">
                    <Layers size={48} className="mb-4 text-slate-500" strokeWidth={1} />
                    <p className="text-slate-400 text-sm">Select &apos;Continue to Mapping&apos; to configure identity swaps.</p>
                  </div>
                ) : (
                  <div className="p-6 flex-1 flex flex-col gap-6 overflow-y-auto custom-scrollbar relative">
                    
                    {/* Advanced Mapping Options Bar */}
                    <div className="flex flex-col sm:flex-row gap-3 bg-white/[0.02] border border-white/5 p-3 rounded-xl shadow-inner">
                      <div className="flex items-center justify-between w-full">
                        <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5"><BrainCircuit size={14} className="text-violet-400" /> Advanced Options</span>
                      </div>
                      <div className="flex gap-2 w-full sm:w-auto">
                        <button 
                          onClick={() => setOcclusionDetection(!occlusionDetection)}
                          className={`flex-1 sm:flex-none px-3 py-1.5 rounded border text-[10px] font-bold uppercase tracking-wider flex items-center justify-center gap-1.5 transition-colors ${occlusionDetection ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-black/50 text-slate-400 border-white/10'}`}
                          title="Auto-adjust blend weights for glasses, hands, microphones"
                        >
                          <Eye size={12} /> Occlusion {occlusionDetection ? 'ON' : 'OFF'}
                        </button>
                        <button 
                          onClick={() => setMicroExpressions(!microExpressions)}
                          className={`flex-1 sm:flex-none px-3 py-1.5 rounded border text-[10px] font-bold uppercase tracking-wider flex items-center justify-center gap-1.5 transition-colors ${microExpressions ? 'bg-violet-500/20 text-violet-400 border-violet-500/30' : 'bg-black/50 text-slate-400 border-white/10'}`}
                          title="Isolate and map target micro-expressions onto source"
                        >
                          <BrainCircuit size={12} /> Expressions {microExpressions ? 'ON' : 'OFF'}
                        </button>
                        {microExpressions && (
                           <button 
                             onClick={() => setShowHeatmap(!showHeatmap)}
                             className={`flex-1 sm:flex-none px-3 py-1.5 rounded border text-[10px] font-bold uppercase tracking-wider flex items-center justify-center gap-1.5 transition-colors ${showHeatmap ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' : 'bg-black/50 text-slate-400 border-white/10'}`}
                             title="Visualize Facial Movement Intensity"
                           >
                             <Flame size={12} /> Heatmap {showHeatmap ? 'ON' : 'OFF'}
                           </button>
                        )}
                      </div>
                    </div>

                    {MOCK_TARGET_FACES.map(target => (
                      <div key={target.id} className={`flex flex-col sm:flex-row items-center gap-4 sm:gap-6 p-4 rounded-xl border transition-all duration-300 ${
                        selectedTargetId === target.id ? 'bg-white/[0.04] border-cyan-500/30' : 'bg-white/[0.01] border-white/5'
                      }`}>
                        
                        {/* Target Face */}
                        <div className="flex flex-col items-center gap-2 w-32 shrink-0">
                          <div className="relative w-20 h-20"><Image src={target.url} alt="Target face" fill referrerPolicy="no-referrer" className="rounded-full border border-white/10 object-cover" /></div>
                          <span className="text-xs font-medium text-slate-400">{target.label}</span>
                        </div>
                        
                        {/* Connection */}
                        <div className="flex-1 flex flex-col items-center justify-center min-w-[100px]">
                          <div className="h-px w-full bg-gradient-to-r from-transparent via-white/20 to-transparent relative flex items-center justify-center">
                            <motion.div 
                              animate={{ x: [0, 10, 0] }} 
                              transition={{ repeat: Infinity, duration: 2 }}
                              className="w-6 h-6 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center absolute"
                            >
                              <ArrowRight size={12} className="text-slate-400" />
                            </motion.div>
                          </div>
                        </div>
                        
                        {/* Source Face Dropzone / Assignment */}
                        <div className="flex flex-col items-center gap-2 w-32 shrink-0">
                          {mappedFaces[target.id] && mappedFaces[target.id] !== 'skip' ? (
                            <div className="relative group cursor-pointer w-20 h-20">
                              {/* Resolve selected source url */}
                              <Image 
                                src={savedSources.find(s => s.id === mappedFaces[target.id])?.url || MOCK_SOURCE_FACES[0].url} 
                                alt="Source face" fill referrerPolicy="no-referrer" className="rounded-full border-2 border-emerald-500/50 object-cover" 
                              />
                              {showHeatmap && microExpressions && (
                                <div 
                                  className="absolute inset-0 rounded-full mix-blend-screen opacity-80 pointer-events-none" 
                                  style={{ background: 'radial-gradient(circle at 50% 60%, rgba(250,204,21,0.7) 0%, rgba(239,68,68,0.5) 40%, rgba(0,0,0,0.8) 80%)' }} 
                                />
                              )}
                              {showHeatmap && microExpressions && (
                                <div className="absolute inset-x-0 bottom-[-16px] flex justify-center pointer-events-none">
                                  <span className="text-[7px] bg-amber-900/90 text-amber-300 px-1 py-0.5 rounded shadow whitespace-nowrap uppercase tracking-widest border border-amber-500/50">Intensity Map</span>
                                </div>
                              )}
                              <button 
                                onClick={() => setIsMasking(true)} 
                                className="absolute bottom-0 right-0 p-1.5 bg-black/80 rounded-full backdrop-blur text-white opacity-0 group-hover:opacity-100 transition-opacity hover:text-emerald-400 z-10 border border-white/20 shadow-lg"
                                title="Paint Blend Mask"
                              >
                                <Brush size={12} />
                              </button>
                              <button 
                                onClick={() => {
                                  const newMap = {...mappedFaces};
                                  delete newMap[target.id];
                                  setMappedFaces(newMap);
                                }}
                                className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                              >
                                <X size={12} />
                              </button>
                            </div>
                          ) : mappedFaces[target.id] === 'skip' ? (
                            <div className="w-20 h-20 rounded-full border border-white/10 bg-white/5 flex items-center justify-center text-slate-500">
                              <span className="text-[10px] font-bold uppercase tracking-widest">Skip</span>
                            </div>
                          ) : (
                            <button 
                              onClick={() => { setActiveTargetForGallery(target.id); setShowGallery(true); }}
                              className="w-20 h-20 rounded-full border border-dashed border-white/30 bg-white/5 hover:bg-white/10 flex flex-col items-center justify-center text-slate-400 hover:text-white hover:border-cyan-400 transition-all group"
                            >
                              <FolderHeart size={18} className="mb-1 group-hover:scale-110 transition-transform" />
                              <span className="text-[9px] uppercase tracking-wider font-semibold">Library</span>
                            </button>
                          )}
                          <div className="flex items-center gap-2">
                            <button 
                              onClick={() => setMappedFaces({...mappedFaces, [target.id]: mappedFaces[target.id] === 'skip' ? 's1' : 'skip'})}
                              className={`text-[10px] font-medium px-2 py-1 rounded transition-colors ${mappedFaces[target.id] === 'skip' ? 'bg-amber-500/20 text-amber-300' : 'bg-white/5 text-slate-400 hover:bg-white/10 hover:text-slate-300'}`}
                            >
                              {mappedFaces[target.id] === 'skip' ? 'Re-assign' : 'Keep Original'}
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* STEP 4: PROCESSING */}
          {currentStep === 4 && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex-1 flex flex-col items-center justify-center max-w-2xl mx-auto w-full"
            >
              <div className="w-full glass-panel rounded-3xl p-8 md:p-12 relative overflow-hidden">
                <div className="text-center mb-10">
                  <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-cyan-500/10 border border-cyan-500/20 mb-6 relative">
                    <Loader2 size={32} className="text-cyan-400 animate-spin" />
                    <div className="absolute inset-0 rounded-full border border-cyan-400 animate-ping opacity-20" />
                  </div>
                  <h2 className="text-2xl font-bold text-white mb-6">Processing Telemetry</h2>
                  <ProgressBar 
                    progress={progress} 
                    statusMsg={processSteps[currentProcessStep]} 
                    eta="00:12s" 
                    theme="cyan" 
                  />
                </div>

                <div className="space-y-4">
                  {processSteps.map((step, idx) => {
                    const isActive = currentProcessStep === idx;
                    const isDone = currentProcessStep > idx;
                    return (
                      <div key={idx} className={`flex items-center gap-4 p-3 rounded-xl transition-all duration-500 ${
                        isActive ? 'bg-white/10 border border-white/20 scale-[1.02]' : 
                        isDone ? 'opacity-50' : 'opacity-30'
                      }`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                          isDone ? 'bg-emerald-500/20 text-emerald-400' : 
                          isActive ? 'bg-cyan-500/20 text-cyan-400' : 'bg-white/5 text-slate-500'
                        }`}>
                          {isDone ? <CheckCircle2 size={16} /> : isActive ? <RefreshCw size={14} className="animate-spin" /> : <Settings2 size={14} />}
                        </div>
                        <span className={`text-sm font-medium ${isActive ? 'text-white' : 'text-slate-300'}`}>{step}</span>
                        {isActive && (
                          <div className="ml-auto flex gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            </motion.div>
          )}

          {/* STEP 5: RESULT SHOWCASE */}
          {currentStep === 5 && (
            <motion.div
              key="step5"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col gap-6 flex-1 h-full"
            >
              <div className="flex items-center justify-between glass-panel px-6 py-4 rounded-2xl">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                    <CheckCircle2 size={24} />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-white leading-tight">Processing Complete</h2>
                    <p className="text-xs text-slate-400 font-mono">1080p • 60fps • Watermark-Free</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <button onClick={() => setCurrentStep(1)} className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 text-sm font-semibold transition-colors">
                    Start New
                  </button>
                  <button 
                    onClick={() => setShowExportPreview(true)}
                    className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-semibold transition-colors flex items-center gap-2"
                  >
                    <Film size={16} /> Export Preview
                  </button>
                  <button 
                    onClick={() => setShowExportSettings(true)}
                    className="px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 transition-colors border border-white/10"
                    title="Export Settings"
                  >
                    <Settings2 size={16} />
                  </button>
                  <button className="px-5 py-2 rounded-lg bg-white text-black hover:bg-slate-200 text-sm font-bold transition-colors flex items-center gap-2 shadow-[0_0_20px_rgba(255,255,255,0.2)]">
                    <Download size={16} /> Full Render
                  </button>
                </div>
              </div>

              {/* Compare Slider Container */}
              <div className="flex-1 glass-panel rounded-2xl overflow-hidden relative min-h-[500px] flex items-center justify-center bg-black/60 group">
                
                {/* Simulated Before Image */}
                
                <Image src="https://picsum.photos/seed/before1/1920/1080" alt="Before" fill referrerPolicy="no-referrer" className="object-contain pointer-events-none" />
                <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded text-xs font-bold text-white/70 tracking-widest uppercase border border-white/10 z-10">Original</div>
                <div className="absolute top-4 right-4 bg-emerald-500/20 backdrop-blur-md px-3 py-1.5 rounded text-xs font-bold text-emerald-400 tracking-widest uppercase border border-emerald-500/30 z-10">Processed</div>

                
                {/* Simulated After Image (Clipped) */}
                <div 
                  className="absolute inset-0 overflow-hidden"
                  style={{ width: `${sliderPos}%` }}
                >
                  <Image 
                    src="https://picsum.photos/seed/after1/1920/1080" 
                    alt="After" fill referrerPolicy="no-referrer" 
                    className="object-contain pointer-events-none" 
                    style={{ filter: `brightness(${brightness}%) contrast(${contrast}%) hue-rotate(${temperature}deg)` }}
                  />
                </div>

                {/* Slider Handle */}
                <div 
                  className="absolute top-0 bottom-0 w-1 bg-white/80 cursor-ew-resize z-20 hover:w-1.5 transition-all shadow-[0_0_10px_rgba(0,0,0,0.5)]"
                  style={{ left: `${sliderPos}%` }}
                  onMouseDown={(e) => {
                    const handleMove = (moveEvent: MouseEvent) => {
                      const rect = (e.currentTarget.parentElement as HTMLElement).getBoundingClientRect();
                      const newPos = Math.max(0, Math.min(100, ((moveEvent.clientX - rect.left) / rect.width) * 100));
                      setSliderPos(newPos);
                    };
                    const handleUp = () => {
                      document.removeEventListener('mousemove', handleMove);
                      document.removeEventListener('mouseup', handleUp);
                    };
                    document.addEventListener('mousemove', handleMove);
                    document.addEventListener('mouseup', handleUp);
                  }}
                >
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-12 bg-white rounded-md shadow-xl flex items-center justify-center gap-1 border border-slate-200">
                    <div className="w-0.5 h-6 bg-slate-300 rounded-full" />
                    <div className="w-0.5 h-6 bg-slate-300 rounded-full" />
                  </div>
                </div>

                <div className="absolute bottom-6 left-6 px-3 py-1.5 rounded-lg bg-black/50 backdrop-blur text-white text-xs font-bold tracking-wider z-10 border border-white/10">
                  AFTER
                </div>
                <div className="absolute bottom-6 right-6 px-3 py-1.5 rounded-lg bg-black/50 backdrop-blur text-slate-400 text-xs font-bold tracking-wider z-10 border border-white/10">
                  BEFORE
                </div>

              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Timeline & QA Controls */}
                <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                    {isPlaying ? <Pause size={16} className="text-cyan-400" /> : <PlayCircle size={16} className="text-cyan-400" />}
                    QA Timeline
                  </h3>
                  
                  <button 
                    onClick={handleSceneDetect}
                    disabled={isDetectingScenes || sceneMarkers.length > 0}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                      sceneMarkers.length > 0 
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                        : isDetectingScenes
                        ? 'bg-white/5 text-slate-400 border border-white/10 cursor-not-allowed'
                        : 'bg-white/10 hover:bg-white/20 text-white border border-white/10'
                    }`}
                  >
                    {isDetectingScenes ? (
                      <><Loader2 size={12} className="animate-spin" /> Analyzing Cuts...</>
                    ) : sceneMarkers.length > 0 ? (
                      <><CheckCircle2 size={12} /> {sceneMarkers.length} Scenes Detected</>
                    ) : (
                      <><Wand2 size={12} /> Auto-Scene Detect</>
                    )}
                  </button>
                </div>

                <div className="relative w-full h-12 bg-black/40 rounded-lg border border-white/5 overflow-hidden flex items-center px-2">
                  {/* Timeline Track */}
                  <div className="relative w-full h-2 bg-white/10 rounded-full cursor-pointer"
                       onMouseDown={(e) => {
                         const handleMove = (moveEvent: MouseEvent) => {
                           const rect = (e.currentTarget.parentElement as HTMLElement).getBoundingClientRect();
                           // Account for the px-2 padding (16px total) if necessary, but this is an approximation
                           const newPos = Math.max(0, Math.min(100, ((moveEvent.clientX - rect.left - 8) / (rect.width - 16)) * 100));
                           setTimelinePos(newPos);
                         };
                         const handleUp = () => {
                           document.removeEventListener('mousemove', handleMove);
                           document.removeEventListener('mouseup', handleUp);
                         };
                         // Initial click positioning
                         const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                         const newPos = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
                         setTimelinePos(newPos);
                         
                         document.addEventListener('mousemove', handleMove);
                         document.addEventListener('mouseup', handleUp);
                       }}>
                    
                    {/* Progress Fill */}
                    <div className="absolute top-0 bottom-0 left-0 bg-cyan-500 rounded-full pointer-events-none" style={{ width: `${timelinePos}%` }} />
                    
                    {/* Playhead */}
                    <div className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-[0_0_10px_rgba(255,255,255,0.8)] pointer-events-none" style={{ left: `${timelinePos}%`, transform: `translate(-50%, -50%)` }} />

                    {/* Scene Markers */}
                    {sceneMarkers.map((marker, idx) => (
                      <div 
                        key={idx}
                        className="absolute top-1/2 -translate-y-1/2 w-1 h-4 bg-emerald-400 rounded-sm shadow-[0_0_8px_rgba(52,211,153,0.8)] pointer-events-none"
                        style={{ left: `${marker}%`, transform: `translate(-50%, -50%)` }}
                        title={`Scene Cut at ${marker}%`}
                      />
                    ))}
                  </div>
                </div>
              </div>

                {/* Post-Processing */}
                <div className="glass-panel rounded-2xl p-6">
                  <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2 mb-6">
                    <SlidersHorizontal size={16} className="text-violet-400" />
                    Color Matching & Post-Processing
                  </h3>
                  
                  <div className="space-y-5">
                    <div>
                      <div className="flex justify-between text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">
                        <span>Brightness</span>
                        <span className="text-white">{brightness}%</span>
                      </div>
                      <input 
                        type="range" min="50" max="150" value={brightness} 
                        onChange={(e) => setBrightness(Number(e.target.value))} 
                        className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-violet-500" 
                      />
                    </div>
                    <div>
                      <div className="flex justify-between text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">
                        <span>Contrast</span>
                        <span className="text-white">{contrast}%</span>
                      </div>
                      <input 
                        type="range" min="50" max="150" value={contrast} 
                        onChange={(e) => setContrast(Number(e.target.value))} 
                        className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-violet-500" 
                      />
                    </div>
                    <div>
                      <div className="flex justify-between text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">
                        <span>Temperature</span>
                        <span className="text-white">{temperature > 0 ? '+' : ''}{temperature}</span>
                      </div>
                      <input 
                        type="range" min="-50" max="50" value={temperature} 
                        onChange={(e) => setTemperature(Number(e.target.value))} 
                        className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-violet-500" 
                      />
                    </div>
                  </div>
                  <div className="mt-6 flex justify-end">
                    <button 
                      onClick={() => { setBrightness(100); setContrast(100); setTemperature(0); }}
                      className="text-xs text-slate-400 hover:text-white transition-colors flex items-center gap-1.5"
                    >
                      <RefreshCw size={12} /> Reset to Default
                    </button>
                  </div>
                </div>
              </div>
              
            </motion.div>
          )}

        </AnimatePresence>
      </main>

      {/* Export Preview Modal */}
      <AnimatePresence>
        {showExportPreview && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
          >
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-slate-900 border border-white/10 p-6 rounded-2xl w-full max-w-2xl flex flex-col gap-4 shadow-2xl"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Film className="text-cyan-400" /> Export Preview
                </h3>
                <button onClick={() => setShowExportPreview(false)} className="text-slate-400 hover:text-white transition-colors">
                  <X size={20} />
                </button>
              </div>
              
              <div className="relative w-full aspect-video bg-black rounded-xl overflow-hidden border border-white/5 flex items-center justify-center">
                {/* Simulated Looping Preview (GIF / Video Snippet) */}
                <Image src="https://picsum.photos/seed/preview_gif/800/450" alt="Preview Snippet" fill className="object-cover opacity-70" referrerPolicy="no-referrer" />
                
                <div className="absolute top-4 left-4 bg-black/50 backdrop-blur px-2 py-1 rounded text-[10px] font-bold text-white tracking-widest uppercase border border-white/10">
                  5s Snippet
                </div>
                
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-16 h-16 rounded-full bg-cyan-500/20 backdrop-blur-md flex items-center justify-center border border-cyan-500/30 text-cyan-400">
                    <Play size={24} fill="currentColor" />
                  </div>
                </div>
              </div>
              
              <p className="text-xs text-slate-400 text-center">
                This is a quick 5-second snippet of the current processed results. Verify quality before committing to a full render.
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>


      {/* Batch Queue Panel */}
      <AnimatePresence>
        {showBatchQueue && (
          <>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm" onClick={() => setShowBatchQueue(false)} />
            <motion.div initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }} transition={{ type: 'spring', damping: 25, stiffness: 200 }} className="fixed top-0 bottom-0 left-0 z-50 w-full sm:w-96 bg-slate-900 border-r border-white/10 shadow-2xl flex flex-col">
              <div className="p-5 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
                <h2 className="text-lg font-bold text-white flex items-center gap-2"><ListOrdered size={18} className="text-emerald-400" /> Batch Queue</h2>
                <button onClick={() => setShowBatchQueue(false)} className="text-slate-400 hover:text-white transition-colors"><X size={20} /></button>
              </div>
              <div className="px-5 py-3 border-b border-white/5 bg-black/40 flex justify-between items-center shadow-inner">
                <div className="flex flex-col">
                  <span className="text-xs font-semibold text-slate-300">Smart Prioritization</span>
                  <span className="text-[9px] text-slate-500">Auto-sequence by resolution & complexity</span>
                </div>
                <button 
                  onClick={() => {
                    const nextVal = !smartPrioritization;
                    setSmartPrioritization(nextVal);
                    if (nextVal) {
                       const sorted = [...batchJobsEx].sort((a, b) => b.name.localeCompare(a.name));
                       setBatchJobsEx(sorted);
                    } else {
                       const original = [...batchJobsEx].sort((a, b) => a.name.localeCompare(b.name));
                       setBatchJobsEx(original);
                    }
                  }}
                  className={`w-9 h-5 rounded-full flex items-center transition-colors p-0.5 ${smartPrioritization ? 'bg-cyan-500' : 'bg-slate-700'}`}
                >
                  <div className={`w-4 h-4 rounded-full bg-white transition-transform ${smartPrioritization ? 'translate-x-4' : 'translate-x-0'} shadow-sm`} />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 custom-scrollbar">
                {batchJobsEx.map(job => (
                  <div key={job.id} className="p-4 rounded-xl border border-white/10 bg-white/5 flex flex-col gap-3 group hover:bg-white/10 transition-colors">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-semibold text-white truncate pr-4">{job.name}</span>
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${job.status === 'Processing' ? 'text-cyan-400 bg-cyan-400/10' : 'text-slate-400 bg-slate-400/10'}`}>{job.status}</span>
                    </div>
                    
                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-medium">
                      <span>ETA: <strong className="text-slate-300">{job.eta}</strong></span>
                      <span>Resource: <strong className="text-slate-300">{job.gpu}</strong></span>
                    </div>

                    <div className="w-full h-1.5 bg-black/50 rounded-full overflow-hidden">
                      <div className={`h-full ${job.status === 'Processing' ? 'bg-cyan-500' : 'bg-slate-500'}`} style={{ width: `${job.progress}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Masking Tool Modal */}
      <AnimatePresence>
        {isMasking && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/90 backdrop-blur-md"
          >
            <div className="bg-slate-900 border border-white/10 p-6 rounded-2xl w-full max-w-2xl flex flex-col gap-4 shadow-2xl">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-white flex items-center gap-2"><Brush className="text-emerald-400" /> Mask Refinement</h3>
                <button onClick={() => setIsMasking(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
              </div>
              <div className="flex justify-between items-start">
                <p className="text-xs text-slate-400 max-w-[70%]">
                  Paint over areas you want to strictly blend or exclude (e.g., hair, glasses, hands). 
                  The mask indicates regions that will be seamlessly passed to the GFPGAN/CodeFormer upscaler.
                </p>
                <label className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-slate-300 cursor-pointer bg-white/5 px-2 py-1.5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors">
                  <input type="checkbox" className="form-checkbox rounded bg-slate-800 border-white/20 text-fuchsia-500 focus:ring-fuchsia-500 focus:ring-offset-slate-900" checked={showMaskOverlay} onChange={() => setShowMaskOverlay(!showMaskOverlay)} />
                  Overlay Focus
                </label>
              </div>
              
              <div 
                className="relative w-full aspect-square sm:aspect-video bg-black rounded-lg overflow-hidden cursor-crosshair border border-white/10 mx-auto"
                onMouseDown={() => setIsDrawing(true)}
                onMouseUp={() => setIsDrawing(false)}
                onMouseLeave={() => setIsDrawing(false)}
                onMouseMove={(e) => {
                  if (isDrawing) {
                    const rect = e.currentTarget.getBoundingClientRect();
                    setMaskPoints(prev => [...prev, { x: ((e.clientX - rect.left)/rect.width)*100, y: ((e.clientY - rect.top)/rect.height)*100 }]);
                  }
                }}
              >
                <Image src="https://picsum.photos/seed/source1/800/450" alt="Masking Source" fill className="object-cover opacity-60" referrerPolicy="no-referrer" />
                {showMaskOverlay ? maskPoints.map((pt, i) => (
                  <div key={i} className="absolute w-8 h-8 bg-fuchsia-500/70 mix-blend-screen rounded-full blur-[2px] pointer-events-none" style={{ left: `${pt.x}%`, top: `${pt.y}%`, transform: 'translate(-50%, -50%)', boxShadow: '0 0 10px rgba(217, 70, 239, 0.5)' }} />
                )) : maskPoints.map((pt, i) => (
                  <div key={i} className="absolute w-8 h-8 bg-emerald-500/40 rounded-full blur-[2px] pointer-events-none" style={{ left: `${pt.x}%`, top: `${pt.y}%`, transform: 'translate(-50%, -50%)' }} />
                ))}
                
                {maskPoints.length === 0 && (
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <span className="bg-black/50 backdrop-blur px-3 py-1.5 rounded-lg text-white/50 text-sm font-bold uppercase tracking-widest border border-white/10">Click & Drag to Paint</span>
                  </div>
                )}
              </div>
              
              <div className="flex justify-between items-center mt-2">
                <button onClick={() => setMaskPoints([])} className="px-4 py-2 rounded-lg bg-white/5 text-white text-sm font-semibold hover:bg-white/10 transition border border-white/10">Clear Mask</button>
                <button onClick={() => setIsMasking(false)} className="px-6 py-2 rounded-lg bg-emerald-600 text-white text-sm font-bold hover:bg-emerald-500 transition shadow-[0_0_15px_rgba(52,211,153,0.3)]">Apply Mask</button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>



      {/* VRAM Diagnostics Panel */}
      <AnimatePresence>
        {showDiagnostics && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }} 
            animate={{ opacity: 1, y: 0 }} 
            exit={{ opacity: 0, y: -10 }} 
            className="absolute top-16 right-4 z-50 bg-slate-900/90 backdrop-blur-xl border border-white/10 rounded-xl p-4 w-72 shadow-2xl flex flex-col gap-4"
          >
            <div className="flex justify-between items-center pb-2 border-b border-white/10">
              <h3 className="text-sm font-bold text-white flex items-center gap-2"><Cpu size={14} className="text-cyan-400" /> System Diagnostics</h3>
              <button onClick={() => setShowDiagnostics(false)} className="text-slate-400 hover:text-white"><X size={14} /></button>
            </div>
            
            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-400">GPU 0 VRAM</span>
                <span className={vramUsage / vramMax > 0.85 ? 'text-red-400' : 'text-emerald-400'}>{vramUsage} / {vramMax} GB</span>
              </div>
              <div className="w-full h-2 bg-black rounded-full overflow-hidden border border-white/5">
                <div 
                  className={`h-full ${vramUsage / vramMax > 0.85 ? 'bg-red-500' : 'bg-emerald-500'}`} 
                  style={{ width: `${(vramUsage / vramMax) * 100}%` }}
                />
              </div>
            </div>
            
            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-400">Model Precision</span>
                <span className="text-slate-200">FP16</span>
              </div>
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-400">Batch Size</span>
                <span className="text-slate-200">4</span>
              </div>
            </div>

            <button 
              onClick={() => {
                setVramUsage(4.1);
                // Notification/alert could go here
              }}
              className="w-full mt-2 py-2 rounded border border-cyan-500/50 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 text-xs font-bold transition-colors flex justify-center items-center gap-2"
            >
              <Zap size={12} /> Optimize Settings
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Source Face Gallery Modal */}
      <AnimatePresence>
        {showGallery && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} className="bg-slate-900 border border-white/10 p-6 rounded-2xl w-full max-w-xl flex flex-col gap-4 shadow-2xl">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-white flex items-center gap-2"><FolderHeart className="text-cyan-400" /> Source Face Library</h3>
                <button onClick={() => setShowGallery(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
              </div>
              
              <div className="flex items-center justify-between">
                <p className="text-xs text-slate-400">Select a saved face to map to the target, or upload a new one.</p>
                <div className="flex gap-3">
                  <button 
                    onClick={() => {
                      // Filter duplicates and low-confidence
                      const seen = new Set();
                      const cleaned = savedSources.filter(s => {
                        const isDup = seen.has(s.url);
                        seen.add(s.url);
                        return !isDup && (s.confidence === undefined || s.confidence >= 0.8);
                      });
                      setSavedSources(cleaned);
                    }}
                    className="flex items-center gap-1.5 px-3 py-1 bg-rose-500/10 border border-rose-500/20 rounded-lg text-[10px] font-bold text-rose-400 hover:bg-rose-500/20 hover:text-rose-300 transition-colors uppercase tracking-widest"
                    title="Remove blurry or duplicate faces"
                  >
                    <Trash2 size={12} /> Clean Library
                  </button>
                  <div className="flex items-center gap-1 bg-black/50 p-1 rounded-lg border border-white/10">
                  <Filter size={12} className="text-slate-500 mx-1" />
                  {['All', 'Male', 'Female'].map(g => (
                    <button 
                      key={g} 
                      onClick={() => setGenderFilter(g)}
                      className={`px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest transition-colors ${genderFilter === g ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-white'}`}
                    >
                      {g}
                    </button>
                  ))}
                </div>
                </div>
              </div>
              
              <div className="grid grid-cols-4 gap-4 mb-2">
                {savedSources.filter(s => genderFilter === 'All' || s.gender === genderFilter).map(source => (
                  <button 
                    key={source.id} 
                    onClick={() => {
                      if(activeTargetForGallery) {
                        setMappedFaces(prev => ({...prev, [activeTargetForGallery]: source.id}));
                      }
                      setShowGallery(false);
                    }}
                    className="flex flex-col items-center gap-2 group"
                  >
                    <div className="relative w-full aspect-square rounded-xl overflow-hidden border-2 border-white/10 group-hover:border-cyan-400 transition-colors">
                      <Image src={source.url} alt={source.label} fill className={`object-cover ${source.confidence && source.confidence < 0.8 ? 'blur-[1px] opacity-40 grayscale mix-blend-luminosity' : ''}`} referrerPolicy="no-referrer" />
                      {source.confidence && source.confidence < 0.8 && (
                        <div className="absolute inset-0 bg-red-900/10 flex flex-col items-center justify-center pointer-events-none">
                          <span className="bg-rose-600/90 text-white text-[8px] font-bold px-1.5 py-0.5 rounded shadow whitespace-nowrap">LOW QUAL</span>
                        </div>
                      )}
                      {source.confidence && source.confidence >= 0.8 && (
                        <div className="absolute bottom-1 right-1 bg-black/70 backdrop-blur-sm text-emerald-400 text-[8px] font-bold px-1.5 py-0.5 rounded shadow">
                          {Math.round(source.confidence * 100)}% Match
                        </div>
                      )}
                    </div>
                    <span className="text-xs font-semibold text-slate-300 group-hover:text-white truncate w-full text-center">{source.label}</span>
                  </button>
                ))}
                
                <button className="flex flex-col items-center justify-center gap-2 w-full aspect-square rounded-xl border-2 border-dashed border-white/20 bg-white/5 hover:bg-white/10 hover:border-cyan-400 transition-colors text-slate-400 hover:text-white">
                  <UploadCloud size={24} />
                  <span className="text-xs font-bold uppercase tracking-wider">New</span>
                </button>
              </div>
              
              {savedMasks.length > 0 && (
                <div className="mt-2 pt-4 border-t border-white/10">
                  <h4 className="text-xs font-bold text-slate-400 mb-3 uppercase tracking-wider flex items-center gap-1.5"><Brush size={12} /> Saved Mask Templates</h4>
                  <div className="flex gap-2 overflow-x-auto pb-2 hide-scrollbar">
                    {savedMasks.map(mask => (
                      <button key={mask.id} className="flex items-center gap-2 px-3 py-1.5 bg-black/50 border border-white/10 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:border-emerald-400 transition-colors shrink-0">
                        <div className="w-4 h-4 rounded bg-emerald-500/20 border border-emerald-500/50" />
                        {mask.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <SwapHistoryModal isOpen={showHistory} onClose={() => setShowHistory(false)} />

      {/* Export Settings Modal */}
      <AnimatePresence>
        {showExportSettings && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} className="bg-slate-900 border border-white/10 p-6 rounded-2xl w-full max-w-sm flex flex-col gap-6 shadow-2xl">
              <div className="flex justify-between items-center border-b border-white/10 pb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2"><Settings2 className="text-violet-400" /> Export Settings</h3>
                <button onClick={() => setShowExportSettings(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
              </div>
              
              <div className="flex flex-col gap-3">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Quality Mode</label>
                <div className="grid grid-cols-2 gap-2">
                  {[ { id: 'fast', label: '⚡ Fast' }, { id: 'hd', label: '✨ High Quality (HD)' } ].map(mode => (
                    <button 
                      key={mode.id}
                      onClick={() => setSetting('qualityMode', mode.id as any)}
                      className={`px-3 py-2 rounded-lg border text-sm font-semibold transition-all ${
                        (present.qualityMode || 'hd') === mode.id ? 'bg-violet-500/20 border-violet-500/50 text-violet-300' : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                      }`}
                    >
                      {mode.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex flex-col gap-3">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Resolution</label>
                <div className="grid grid-cols-2 gap-2">
                  {['1920x1080', '3840x2160', '1280x720'].map(res => (
                    <button 
                      key={res}
                      onClick={() => setSetting('resolution', res)}
                      className={`px-3 py-2 rounded-lg border text-sm font-semibold transition-all ${
                        present.resolution === res ? 'bg-violet-500/20 border-violet-500/50 text-violet-300' : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                      }`}
                    >
                      {res}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-3">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Frame Rate</label>
                <div className="flex gap-2">
                  {[24, 30, 60].map(fps => (
                    <button 
                      key={fps}
                      onClick={() => setSetting('frameRate', fps)}
                      className={`flex-1 py-2 rounded-lg border text-sm font-semibold transition-all ${
                        present.frameRate === fps ? 'bg-violet-500/20 border-violet-500/50 text-violet-300' : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                      }`}
                    >
                      {fps} fps
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-3">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Compression</label>
                <div className="grid grid-cols-2 gap-2">
                  {['low', 'medium', 'high', 'lossless'].map(comp => (
                    <button 
                      key={comp}
                      onClick={() => setSetting('compression', comp)}
                      className={`px-3 py-2 rounded-lg border text-sm font-semibold capitalize transition-all ${
                        present.compression === comp ? 'bg-violet-500/20 border-violet-500/50 text-violet-300' : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                      }`}
                    >
                      {comp}
                    </button>
                  ))}
                </div>
              </div>
              
              <div className="pt-2">
                <button onClick={() => setShowExportSettings(false)} className="w-full py-2.5 rounded-lg bg-white text-black font-bold text-sm hover:bg-slate-200 transition-colors">
                  Save Configuration
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Shortcuts Cheat Sheet */}
      <AnimatePresence>
        {showShortcuts && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" onClick={() => setShowShortcuts(false)}>
            <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 20, opacity: 0 }} className="bg-slate-900 border border-white/10 p-6 rounded-2xl w-full max-w-md flex flex-col gap-4 shadow-2xl" onClick={e => e.stopPropagation()}>
              <div className="flex justify-between items-center border-b border-white/10 pb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2"><Keyboard className="text-cyan-400" /> Keyboard Shortcuts</h3>
                <button onClick={() => setShowShortcuts(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
              </div>
              <div className="flex flex-col gap-3 py-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-300">Play/Pause Timeline</span>
                  <div className="flex gap-1"><kbd className="px-2 py-1 bg-white/10 rounded border border-white/20 text-xs font-mono text-white">Space</kbd></div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-300">Start Processing</span>
                  <div className="flex gap-1">
                    <kbd className="px-2 py-1 bg-white/10 rounded border border-white/20 text-xs font-mono text-white">Ctrl</kbd>
                    <span className="text-slate-500">+</span>
                    <kbd className="px-2 py-1 bg-white/10 rounded border border-white/20 text-xs font-mono text-white">Enter</kbd>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-300">Toggle Landmarks</span>
                  <div className="flex gap-1"><kbd className="px-2 py-1 bg-white/10 rounded border border-white/20 text-xs font-mono text-white">L</kbd></div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      
    </div>
  );
}
