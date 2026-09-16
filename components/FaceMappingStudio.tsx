/* eslint-disable react-hooks/set-state-in-effect */
'use client';
import React, { useState, useEffect } from 'react';
import { UploadCloud, ImageIcon, Film, Loader2, CheckCircle2, User, X, ChevronRight, Play, Wand2 } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import ProcessingDiagnostics from './ProcessingDiagnostics';
import ProgressBar from './ProgressBar';
import ProcessingOverlay from './ProcessingOverlay';
import BeforeAfterPreview from './BeforeAfterPreview';
import { auth, db } from '../lib/firebase';
import { doc, setDoc } from 'firebase/firestore';
import LandmarkAdjustmentOverlay from './LandmarkAdjustmentOverlay';
import { Settings } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const getUseCuda = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('neoFace_useCuda') !== 'false';
  }
  return true;
};


interface DetectedFace {
  face_id: string;
  embedding: number[];
  thumbnail_url: string;
  bbox: number[];
  frame_idx: number;
}

interface SourceMapping {
  previewUrl: string;
  uploadedPath: string;
  sourceBbox?: number[];
}

export default function FaceMappingStudio() {
  const [targetFile, setTargetFile] = useState<File | null>(null);
  const [targetPreviewUrl, setTargetPreviewUrl] = useState<string | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [isAutoMapping, setIsAutoMapping] = useState(false);
  const [targetPath, setTargetPath] = useState<string | null>(null);
  const [isVideo, setIsVideo] = useState(false);
  const [detectedFaces, setDetectedFaces] = useState<DetectedFace[]>([]);
  
  // Mapping from target face_id to source image data
  const [faceMappings, setFaceMappings] = useState<Record<string, SourceMapping>>({});
  
  const [maskModifiers, setMaskModifiers] = useState<Record<string, {expansion: number, erosion: number}>>({});
  const [landmarkModifiers, setLandmarkModifiers] = useState<Record<string, { scale: number, rotate: number, x: number, y: number }>>({});
  const [activeFaceForAdjust, setActiveFaceForAdjust] = useState<string | null>(null);
  const [mediaSize, setMediaSize] = useState<{width: number, height: number} | null>(null);
  
  const [jobId, setJobId] = useState<string | null>(null);
  const [qualityMode, setQualityMode] = useState<'hd' | 'fast'>('hd');
  const [faceRestoration, setFaceRestoration] = useState(false);
  const [exportProfile, setExportProfile] = useState<'web' | 'high' | 'lossless'>('high');
  const [progress, setProgress] = useState(0);
  const [statusMsg, setStatusMsg] = useState('');
  const [resultPath, setResultPath] = useState<string | null>(null);
  const [jobMetrics, setJobMetrics] = useState<{ process_time_s: number, frames: number, fps: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sourceSelectionModal, setSourceSelectionModal] = useState<{
    targetFaceId: string;
    sourcePath: string;
    previewUrl: string;
    faces: any[];
  } | null>(null);
  const [sourceModalLoading, setSourceModalLoading] = useState<string | null>(null);
  const [sourceModalSize, setSourceModalSize] = useState<{width: number, height: number} | null>(null);



  // Auto-Save: Load session from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('neoFace_session');
    if (saved) {
      try {
        const session = JSON.parse(saved);
        if (session.targetPath) {
          setTargetPath(session.targetPath);
          setTargetPreviewUrl(`${API_URL}/uploads/${session.targetPath.split('/').pop()}`);
          setIsVideo(session.isVideo || false);
        }
        if (session.detectedFaces) setDetectedFaces(session.detectedFaces);
        
        if (session.faceMappings) {
           const restoredMappings: Record<string, SourceMapping> = {};
           Object.keys(session.faceMappings).forEach(key => {
             const mapping = session.faceMappings[key];
             restoredMappings[key] = {
               uploadedPath: mapping.uploadedPath,
               previewUrl: `${API_URL}/uploads/${mapping.uploadedPath.split('/').pop()}`
             };
           });
           setFaceMappings(restoredMappings);
        }
        
        if (session.maskModifiers) setMaskModifiers(session.maskModifiers);
        if (session.landmarkModifiers) setLandmarkModifiers(session.landmarkModifiers);
        if (session.qualityMode) setQualityMode(session.qualityMode);
        if (session.faceRestoration !== undefined) setFaceRestoration(session.faceRestoration);
        if (session.exportProfile) setExportProfile(session.exportProfile);
      } catch (err) {
        console.error("Failed to parse session", err);
      }
    }
  }, []);

  // Auto-Save: Save session to localStorage on changes
  useEffect(() => {
    if (targetPath) {
      const session = {
        targetPath,
        isVideo,
        detectedFaces,
        faceMappings,
        maskModifiers,
        landmarkModifiers,
        qualityMode,
        faceRestoration,
        exportProfile
      };
      localStorage.setItem('neoFace_session', JSON.stringify(session));
    }
  }, [targetPath, isVideo, detectedFaces, faceMappings, maskModifiers, landmarkModifiers, qualityMode, faceRestoration, exportProfile]);

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = async (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      // Start Swap on Ctrl+Enter
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (targetPath && detectedFaces.length > 0 && !jobId && Object.keys(faceMappings).length > 0) {
          startSwap();
        }
        return;
      }

      // Undo on Ctrl+Z
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
        e.preventDefault();
        setFaceMappings({});
        setMaskModifiers({});
        return;
      }

      // Save to History on Ctrl+S
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        if (resultPath && auth.currentUser) {
          try {
            const uid = auth.currentUser.uid;
            const historyId = Date.now().toString() + Math.random().toString(36).substring(2, 9);
            const historyRef = doc(db, 'users', uid, 'swapHistory', historyId);
            const finalResultPath = resultPath.startsWith('http') ? resultPath : `${API_URL}/outputs/${resultPath.split('/').pop()}`;
            await setDoc(historyRef, {
              id: historyId,
              userId: uid,
              resultUrl: finalResultPath,
              isVideo: isVideo,
              createdAt: Date.now(),
              qualityMode: qualityMode,
              facesSwapped: Object.keys(faceMappings).length
            });
            console.log("Saved to history via shortcut");
          } catch (err) {
            console.error("Failed to save history", err);
          }
        }
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [targetPath, detectedFaces, jobId, faceMappings, resultPath, isVideo, qualityMode]);

  const { getRootProps: getTargetProps, getInputProps: getTargetInputProps, isDragActive: isTargetActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) handleTargetUpload(acceptedFiles[0]);
    },
    accept: { 'image/*': ['.jpeg', '.jpg', '.png'], 'video/*': ['.mp4', '.mov'] },
    maxFiles: 1
  });

  const handleTargetUpload = async (file: File | null) => {
    if (!file) {
      setTargetFile(null);
      setTargetPreviewUrl(null);
      setTargetPath(null);
      setDetectedFaces([]);
      setFaceMappings({});
      setMaskModifiers({});
      setLandmarkModifiers({});
      setResultPath(null);
      setJobMetrics(null);
      setJobId(null);
      setError(null);
      setMediaSize(null);
      localStorage.removeItem('neoFace_session');
      return;
    }
    setTargetFile(file);
    setTargetPreviewUrl(URL.createObjectURL(file));
    setDetectedFaces([]);
    setFaceMappings({});
    setMaskModifiers({});
    setLandmarkModifiers({});
    setResultPath(null);
    setJobMetrics(null);
    setJobId(null);
    setError(null);
    setMediaSize(null);
  };

  const startDetection = async () => {
    if (!targetFile) return;
    setIsDetecting(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', targetFile);
      formData.append('use_cuda', getUseCuda().toString());
      const res = await fetch(`${API_URL}/api/target/detect`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Failed to detect faces');
      const data = await res.json();
      setTargetPath(data.target_path);
      setIsVideo(data.is_video);
      setDetectedFaces(data.faces);
      
      const initialModifiers: Record<string, {expansion: number, erosion: number}> = {};
      data.faces.forEach((f: any) => {
        initialModifiers[f.face_id] = { expansion: 0, erosion: 0 };
      });
      setMaskModifiers(initialModifiers);
    } catch (err) {
      console.error(err);
      setError("Detection failed. Make sure backend is running.");
    } finally {
      setIsDetecting(false);
    }
  };

  const handleSourceUpload = async (faceId: string, file: File) => {
    setSourceModalLoading(faceId);
    const previewUrl = URL.createObjectURL(file);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('use_cuda', getUseCuda().toString());
    
    try {
      // Use the detect endpoint to find all faces in the source image
      const res = await fetch(`${API_URL}/api/target/detect`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error('Detection failed');
      const data = await res.json();
      
      if (!data.faces || data.faces.length === 0) {
        alert("No faces detected in the uploaded image.");
        setSourceModalLoading(null);
        return;
      }
      
      if (data.faces.length === 1) {
        // If only 1 face, auto select it
        setFaceMappings(prev => ({
          ...prev,
          [faceId]: { previewUrl, uploadedPath: data.target_path, sourceBbox: data.faces[0].bbox }
        }));
      } else {
        // Multiple faces found, open selection modal
        setSourceSelectionModal({
          targetFaceId: faceId,
          sourcePath: data.target_path,
          previewUrl,
          faces: data.faces
        });
      }
    } catch (err) {
      console.error(err);
      alert("Failed to process source image");
    } finally {
      setSourceModalLoading(null);
    }
  };

  const handleAutoMap = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    
    setIsAutoMapping(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const embeddings: Record<string, number[]> = {};
      detectedFaces.forEach(f => {
        embeddings[f.face_id] = f.embedding;
      });
      formData.append('target_embeddings', JSON.stringify(embeddings));
      formData.append('use_cuda', getUseCuda().toString());
      
      const res = await fetch(`${API_URL}/api/source/automap`, {
        method: 'POST',
        body: formData
      });
      
      if (!res.ok) throw new Error('Auto-map failed');
      const data = await res.json();
      
      setFaceMappings(prev => ({
        ...prev,
        ...data.mappings
      }));
    } catch (err) {
      console.error(err);
      setError("Auto-mapping failed. Make sure backend is running.");
    } finally {
      setIsAutoMapping(false);
    }
  };

  async function startSwap() {
    if (!targetPath) return;
    setJobId('starting');
    setProgress(0);
    setError(null);

    try {
      const mappingDict: Record<string, string> = {};
      const embeddingsDict: Record<string, number[]> = {};
      const modifiersDict: Record<string, { expansion: number, erosion: number }> = {};
      const sourceBboxesDict: Record<string, number[]> = {};
      
      detectedFaces.forEach(f => {
        if (faceMappings[f.face_id]?.uploadedPath) {
          mappingDict[f.face_id] = faceMappings[f.face_id].uploadedPath;
          embeddingsDict[f.face_id] = f.embedding;
          modifiersDict[f.face_id] = {
            expansion: (maskModifiers[f.face_id]?.expansion || 0) / 100,
            erosion: (maskModifiers[f.face_id]?.erosion || 0) / 100
          };
          if (faceMappings[f.face_id].sourceBbox) {
             sourceBboxesDict[f.face_id] = faceMappings[f.face_id].sourceBbox!;
          }
        }
      });
      
      if (Object.keys(mappingDict).length === 0) {
        throw new Error("Please map at least one face.");
      }

      const formData = new FormData();
      formData.append('target_path', targetPath);
      formData.append('is_video', isVideo.toString());
      formData.append('quality_mode', qualityMode);
      formData.append('face_restoration', faceRestoration.toString());
      formData.append('export_profile', exportProfile);
      formData.append('use_cuda', getUseCuda().toString());
      formData.append('mapping_data', JSON.stringify({
        mapping: mappingDict,
        embeddings: embeddingsDict,
        modifiers: modifiersDict,
        landmark_modifiers: landmarkModifiers,
        source_bboxes: sourceBboxesDict
      }));

      const res = await fetch(`${API_URL}/api/target/swap`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error('Failed to dispatch multi-swap job');
      const data = await res.json();
      setJobId(data.task_id);
      pollStatus(data.task_id);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to start swap.");
      setJobId(null);
    }
  };

  const pollStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/api/jobs/${id}`);
        const data = await res.json();
        
        if (data.state === 'PROGRESS') {
          setProgress(data.progress);
          setStatusMsg(data.status_msg);
        } else if (data.state === 'SUCCESS') {
          clearInterval(interval);
          setProgress(100);
          setStatusMsg("Completed");
          setResultPath(data.result.output_path);
          if (data.result.metrics) {
            setJobMetrics(data.result.metrics);
          }
          setJobId(null);
        } else if (data.state === 'FAILURE') {
          clearInterval(interval);
          setJobId(null);
          setError(data.error);
        }
      } catch (err) {
        clearInterval(interval);
      }
    }, 2000);
  };

  const onMediaLoad = (e: any) => {
    if (isVideo || targetFile?.type.startsWith('video')) {
      setMediaSize({ width: e.target.videoWidth, height: e.target.videoHeight });
    } else {
      setMediaSize({ width: e.target.naturalWidth, height: e.target.naturalHeight });
    }
  };

  return (
    <div className="w-full space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          1. Upload Target Media
        </h2>
        
        {!targetPreviewUrl ? (
          <div 
            {...getTargetProps()} 
            className={`border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer transition-all duration-200 
              ${isTargetActive ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50'}`}
          >
            <input {...getTargetInputProps()} />
            <UploadCloud className="mx-auto h-16 w-16 text-slate-400 mb-4" />
            <h3 className="text-xl font-semibold text-slate-700">Drop Target Photo or Video</h3>
            <p className="text-slate-500 mt-2">MP4, MOV, JPG, PNG up to 1GB</p>
          </div>
        ) : (
          <div className="flex flex-col md:flex-row gap-8 items-start">
            <div className="relative w-full md:w-1/2 aspect-video bg-slate-100 rounded-2xl flex items-center justify-center border border-slate-200">
              <div className="relative inline-block max-w-full max-h-full">
                {isVideo ? (
                  <video src={targetPreviewUrl!} className="max-h-full max-w-full block" controls onLoadedMetadata={onMediaLoad} />
                ) : (
                  /* eslint-disable-next-line @next/next/no-img-element */
                  <img src={targetPreviewUrl!} className="max-h-full max-w-full object-contain block" alt="Target" onLoad={onMediaLoad} />
                )}
                
                {/* BBox Overlays */}
                {mediaSize && detectedFaces.map(face => {
                  const width = face.bbox[2] - face.bbox[0];
                  const height = face.bbox[3] - face.bbox[1];
                  
                  // Calculate dynamic padding based on sliders
                  const fExpansion = maskModifiers[face.face_id]?.expansion || 0;
                  const fErosion = maskModifiers[face.face_id]?.erosion || 0;
                  const expansionPx = width * (fExpansion / 100) * 0.5;
                  const erosionPx = width * (fErosion / 100) * 0.5;
                  const netPadding = expansionPx - erosionPx;
                  
                  const newX1 = face.bbox[0] - netPadding;
                  const newY1 = face.bbox[1] - netPadding;
                  const newW = width + (netPadding * 2);
                  const newH = height + (netPadding * 2);

                  const tmods = landmarkModifiers[face.face_id] || { scale: 1, rotate: 0, x: 0, y: 0 };
                  const transformStyle = `translate(${tmods.x}px, ${tmods.y}px) rotate(${tmods.rotate}deg) scale(${tmods.scale})`;

                  return (
                    <div 
                      key={face.face_id}
                      className={`absolute border-2 transition-all duration-150 group ${activeFaceForAdjust === face.face_id ? 'border-emerald-500 bg-emerald-500/20 z-40' : 'border-indigo-500 bg-indigo-500/20 z-30'}`}
                      style={{
                        left: `${(newX1 / mediaSize.width) * 100}%`,
                        top: `${(newY1 / mediaSize.height) * 100}%`,
                        width: `${(newW / mediaSize.width) * 100}%`,
                        height: `${(newH / mediaSize.height) * 100}%`,
                        transform: transformStyle
                      }}
                    >
                      <span className="absolute -top-6 left-0 bg-indigo-600 text-white text-xs font-bold px-1.5 py-0.5 rounded shadow-sm whitespace-nowrap">
                        Face {detectedFaces.findIndex(f => f.face_id === face.face_id) + 1}
                      </span>
                      <button 
                        onClick={() => setActiveFaceForAdjust(activeFaceForAdjust === face.face_id ? null : face.face_id)}
                        className="absolute -top-8 right-0 bg-white text-slate-800 hover:bg-slate-100 p-1 rounded-full shadow-md z-50 pointer-events-auto"
                      >
                        <Settings size={14} />
                      </button>
                      
                      {activeFaceForAdjust === face.face_id && (
                        <LandmarkAdjustmentOverlay 
                          faceId={face.face_id}
                          modifiers={tmods}
                          onChange={(mods) => setLandmarkModifiers(prev => ({ ...prev, [face.face_id]: mods }))}
                          onClose={() => setActiveFaceForAdjust(null)}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
              <button 
                onClick={() => handleTargetUpload(null)}
                className="absolute top-4 right-4 bg-white/90 p-2 rounded-full shadow-md text-slate-700 hover:text-red-600 transition-colors z-10"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="w-full md:w-1/2 flex flex-col justify-center">
              <h3 className="text-lg font-semibold text-slate-800 mb-2">Media Ready</h3>
              <p className="text-slate-500 mb-6 text-sm">
                Next, we will analyze this media to find all unique faces present. This may take a few moments for longer videos.
              </p>
              <button
                onClick={startDetection}
                disabled={isDetecting || detectedFaces.length > 0}
                className="px-8 py-4 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-xl font-bold shadow-md transition-all flex items-center justify-center gap-2"
              >
                {isDetecting ? <Loader2 className="animate-spin" size={20} /> : <User size={20} />}
                {isDetecting ? "Analyzing Faces..." : detectedFaces.length > 0 ? "Faces Detected" : "Detect Faces"}
              </button>
              {error && <p className="text-red-500 mt-4 text-sm font-medium">{error}</p>}
            </div>
          </div>
        )}
      </div>

      {detectedFaces.length > 0 && (
        <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200 animate-in fade-in zoom-in-95 duration-500">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-8">
            <div>
              <h2 className="text-2xl font-bold mb-2">2. Map Source Faces</h2>
              <p className="text-slate-500 max-w-2xl">
                We found {detectedFaces.length} unique {detectedFaces.length === 1 ? 'person' : 'people'} in your target media. 
                Upload a source face for anyone you want to swap. Unmapped faces will be ignored.
              </p>
            </div>
            
            <div className="flex-shrink-0">
              <input type="file" id="automap-upload" className="hidden" accept="image/*" onChange={handleAutoMap} />
              <label htmlFor="automap-upload" className={`px-5 py-3 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded-xl font-bold text-sm transition-colors border border-indigo-200 shadow-sm flex items-center justify-center gap-2 w-full md:w-auto ${isAutoMapping ? 'cursor-not-allowed opacity-70' : 'cursor-pointer'}`}>
                {isAutoMapping ? <Loader2 className="animate-spin" size={18} /> : <Wand2 size={18} />}
                {isAutoMapping ? "Mapping..." : "Auto-Map from Photo"}
              </label>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {detectedFaces.map((face, idx) => (
              <FaceMappingCard 
                key={face.face_id} 
                face={face} 
                index={idx}
                mapping={faceMappings[face.face_id]}
                isLoading={sourceModalLoading === face.face_id}
                maskExpansion={maskModifiers[face.face_id]?.expansion || 0}
                maskErosion={maskModifiers[face.face_id]?.erosion || 0}
                onMaskChange={(type: 'expansion'|'erosion', val: number) => {
                  setMaskModifiers(p => ({
                    ...p,
                    [face.face_id]: { ...p[face.face_id], [type]: val }
                  }));
                }}
                onUpload={(file: File) => handleSourceUpload(face.face_id, file)}
                onClear={() => setFaceMappings(p => { const next={...p}; delete next[face.face_id]; return next; })}
              />
            ))}
          </div>

          <div className="pt-6 border-t border-slate-100 flex flex-col gap-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-slate-50 p-6 rounded-2xl border border-slate-200">
              <div className="flex flex-col gap-3">
                <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                  <Wand2 size={18} className="text-indigo-500" />
                  Post-Processing
                </h3>
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className={`w-10 h-6 rounded-full transition-colors flex items-center px-1 ${faceRestoration ? 'bg-indigo-500' : 'bg-slate-300'}`}>
                    <div className={`w-4 h-4 bg-white rounded-full transition-transform ${faceRestoration ? 'translate-x-4' : 'translate-x-0'}`} />
                  </div>
                  <input type="checkbox" className="hidden" checked={faceRestoration} onChange={(e) => setFaceRestoration(e.target.checked)} />
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-slate-700 group-hover:text-indigo-600 transition-colors">AI Face Restoration</span>
                    <span className="text-xs text-slate-500">Enhance clarity and detail of swapped faces using CodeFormer pass</span>
                  </div>
                </label>
              </div>
              
              <div className="flex flex-col gap-3">
                <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                  <Film size={18} className="text-indigo-500" />
                  Export Profile
                </h3>
                <div className="flex bg-white border border-slate-200 rounded-xl p-1 shadow-sm">
                  <button 
                    onClick={() => setExportProfile('web')}
                    className={`flex-1 px-3 py-2 rounded-lg text-xs font-bold transition-all ${exportProfile === 'web' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50'}`}
                  >
                    Web Optimized
                  </button>
                  <button 
                    onClick={() => setExportProfile('high')}
                    className={`flex-1 px-3 py-2 rounded-lg text-xs font-bold transition-all ${exportProfile === 'high' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50'}`}
                  >
                    High Quality
                  </button>
                  <button 
                    onClick={() => setExportProfile('lossless')}
                    className={`flex-1 px-3 py-2 rounded-lg text-xs font-bold transition-all ${exportProfile === 'lossless' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50'}`}
                  >
                    Lossless
                  </button>
                </div>
              </div>
            </div>

            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
              <div className="text-sm font-medium text-slate-600">
                <span className="text-indigo-600 font-bold">{Object.keys(faceMappings).length}</span> of {detectedFaces.length} faces mapped
              </div>
              
              <button
                onClick={startSwap}
                disabled={Object.keys(faceMappings).length === 0 || !!jobId}
                className="w-full md:w-auto px-10 py-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:text-slate-500 text-white rounded-xl font-bold text-lg shadow-md transition-all flex items-center justify-center gap-2"
              >
                {jobId ? <Loader2 className="animate-spin" size={24} /> : <Play size={24} />}
                {jobId ? "Processing Multi-Swap..." : "Start Multi-Swap"}
              </button>
            </div>
          </div>

          <ProcessingOverlay
            isVisible={!!jobId}
            progress={progress}
            statusMsg={statusMsg || "Initializing pipeline..."}
            theme="indigo"
          />

          {resultPath && targetPreviewUrl && (
            <div className="flex flex-col gap-4 mt-8 animate-in slide-in-from-bottom-4">
              <div className="flex items-center gap-3 text-emerald-700 font-semibold text-lg mb-2">
                <CheckCircle2 size={28} /> Multi-Swap Completed
              </div>
              
              <BeforeAfterPreview 
                originalSrc={targetPreviewUrl}
                resultSrc={resultPath.startsWith('http') ? resultPath : `${API_URL}/outputs/${resultPath.split('/').pop()}`}
                isVideo={isVideo}
                downloadName={`neoface_multiswap.${resultPath.split('.').pop()}`}
              />
              
              {jobMetrics && (
                <div className="mt-4">
                  <ProcessingDiagnostics metrics={jobMetrics} />
                </div>
              )}
            </div>
          )}
        </div>
      )}


    </div>
  );
}

function FaceMappingCard({ face, index, mapping, maskExpansion, maskErosion, onMaskChange, onUpload, onClear, isLoading }: any) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (files) => { if (files.length > 0) onUpload(files[0]); },
    accept: { 'image/*': ['.jpeg', '.jpg', '.png'] },
    maxFiles: 1
  });

  // Calculate mask overlay sizing based on expansion/erosion
  // The backend thumbnail uses a margin of 0.2, meaning the face width is ~71.4% of the thumbnail.
  const baseW = 71.4;
  
  const expansionPct = (maskExpansion / 100) * 0.5 * baseW;
  const erosionPct = (maskErosion / 100) * 0.5 * baseW;
  const netPadding = expansionPct - erosionPct;
  
  const maskRadius = Math.max(0, (baseW / 2) + netPadding);

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 flex flex-col shadow-sm">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-bold text-sm">
          {index + 1}
        </div>
        <h4 className="font-semibold text-slate-800">Target Person {index + 1}</h4>
      </div>
      
      <div className="flex flex-col gap-4">
        {/* Target Thumbnail */}
        <div className="relative aspect-square w-full max-w-[160px] mx-auto rounded-xl overflow-hidden border-2 border-slate-200 bg-white shadow-inner group">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={`${API_URL}${face.thumbnail_url}`} alt="Target Face" className="w-full h-full object-cover" />
          
          {/* Mask Overlay */}
          <svg 
            className="absolute inset-0 w-full h-full pointer-events-none opacity-80 group-hover:opacity-100 z-10" 
            viewBox="0 0 100 100"
          >
            <circle 
              cx="50" 
              cy="50" 
              r={maskRadius} 
              fill="rgba(99, 102, 241, 0.2)" 
              stroke="rgba(99, 102, 241, 0.8)" 
              strokeWidth="2"
              className="transition-all duration-200"
            />
          </svg>

          <div className="absolute bottom-0 inset-x-0 bg-black/50 text-white text-[10px] py-1 text-center font-medium backdrop-blur-sm z-20">
            Target Face
          </div>
        </div>
        
        <div className="flex justify-center text-slate-300">
          <ChevronRight size={24} className="rotate-90 md:rotate-0" />
        </div>

        {/* Source Upload/Preview */}
        {!mapping ? (
          <div 
            {...getRootProps()} 
            className={`aspect-square w-full max-w-[160px] mx-auto rounded-xl border-2 border-dashed flex flex-col items-center justify-center cursor-pointer transition-colors text-center p-4
              ${isDragActive ? 'border-indigo-500 bg-indigo-50 text-indigo-600' : 'border-slate-300 bg-white text-slate-400 hover:border-indigo-400 hover:bg-slate-50 hover:text-indigo-500'}`}
          >
            <input {...getInputProps()} />
            <UploadCloud size={32} className="mb-2" />
            <span className="text-xs font-medium">Upload Source</span>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            <div className="relative aspect-square w-full max-w-[160px] mx-auto rounded-xl overflow-hidden border-2 border-indigo-500 shadow-md group bg-white">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={mapping.previewUrl} alt="Source Face" className="w-full h-full object-cover" />
              <div className="absolute bottom-0 inset-x-0 bg-indigo-600/90 text-white text-[10px] py-1 text-center font-bold backdrop-blur-sm">
                Source Face
              </div>
              
              {!mapping.uploadedPath && (
                <div className="absolute inset-0 bg-white/60 flex items-center justify-center">
                  <Loader2 className="animate-spin text-indigo-600" size={24} />
                </div>
              )}
              
              <button 
                onClick={(e) => { e.stopPropagation(); onClear(); }}
                className="absolute top-2 right-2 bg-black/60 p-1.5 rounded-full text-white hover:bg-red-500 transition-colors opacity-0 group-hover:opacity-100"
              >
                <X size={14} />
              </button>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm flex flex-col gap-3">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Expansion</label>
                  <span className="text-[10px] font-bold text-indigo-600 bg-indigo-50 px-1.5 rounded">{maskExpansion}%</span>
                </div>
                <input 
                  type="range" min="0" max="100" 
                  value={maskExpansion} 
                  onChange={e => onMaskChange('expansion', Number(e.target.value))} 
                  className="w-full h-1 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600" 
                />
              </div>
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Erosion</label>
                  <span className="text-[10px] font-bold text-indigo-600 bg-indigo-50 px-1.5 rounded">{maskErosion}%</span>
                </div>
                <input 
                  type="range" min="0" max="100" 
                  value={maskErosion} 
                  onChange={e => onMaskChange('erosion', Number(e.target.value))} 
                  className="w-full h-1 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600" 
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {sourceSelectionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl w-full max-w-4xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <div>
                <h3 className="text-xl font-bold text-slate-800">Multiple Faces Detected</h3>
                <p className="text-sm text-slate-500 mt-1">Select the specific face you want to use as the source.</p>
              </div>
              <button 
                onClick={() => { setSourceSelectionModal(null); setSourceModalSize(null); }}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1 flex flex-col items-center">
              <div className="relative inline-block border-2 border-slate-200 rounded-xl overflow-hidden bg-slate-100">
                <img 
                  id="source-modal-img"
                  src={sourceSelectionModal.previewUrl} 
                  alt="Source" 
                  className="max-h-[60vh] max-w-full object-contain block"
                  onLoad={(e: any) => setSourceModalSize({width: e.target.naturalWidth, height: e.target.naturalHeight})}
                />
                
                {sourceSelectionModal.faces.map((face, idx) => {
                  return (
                    <div
                      key={face.face_id}
                      onClick={() => {
                        setFaceMappings(prev => ({
                          ...prev,
                          [sourceSelectionModal.targetFaceId]: {
                            previewUrl: sourceSelectionModal.previewUrl,
                            uploadedPath: sourceSelectionModal.sourcePath,
                            sourceBbox: face.bbox
                          }
                        }));
                        setSourceSelectionModal(null); setSourceModalSize(null);
                      }}
                      className="absolute border-4 border-emerald-500 cursor-pointer hover:bg-emerald-500/20 transition-all flex items-center justify-center group"
                      style={sourceModalSize ? {
                        left: `${(face.bbox[0] / sourceModalSize.width) * 100}%`,
                        top: `${(face.bbox[1] / sourceModalSize.height) * 100}%`,
                        width: `${((face.bbox[2] - face.bbox[0]) / sourceModalSize.width) * 100}%`,
                        height: `${((face.bbox[3] - face.bbox[1]) / sourceModalSize.height) * 100}%`,
                      } : { display: 'none' }}
                    >
                      <div className="absolute -top-10 bg-emerald-600 text-white font-bold px-3 py-1 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                        Select Face {idx + 1}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            
            <div className="p-6 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
              <button 
                onClick={() => { setSourceSelectionModal(null); setSourceModalSize(null); }}
                className="px-6 py-2.5 rounded-xl font-bold text-slate-600 hover:bg-slate-200 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
