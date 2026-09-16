import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

# 1. Import LandmarkAdjustmentOverlay and Settings icon
import_insert = "import BeforeAfterPreview from './BeforeAfterPreview';\nimport { auth, db } from '../lib/firebase';\nimport { doc, setDoc } from 'firebase/firestore';"
import_replacement = import_insert + "\nimport LandmarkAdjustmentOverlay from './LandmarkAdjustmentOverlay';\nimport { Settings } from 'lucide-react';"
code = code.replace(import_insert, import_replacement)

# 2. Add landmarkModifiers state
state_insert = "  const [maskModifiers, setMaskModifiers] = useState<Record<string, {expansion: number, erosion: number}>>({});"
state_replacement = state_insert + "\n  const [landmarkModifiers, setLandmarkModifiers] = useState<Record<string, { scale: number, rotate: number, x: number, y: number }>>({});\n  const [activeFaceForAdjust, setActiveFaceForAdjust] = useState<string | null>(null);"
code = code.replace(state_insert, state_replacement)

# 3. Add to formData payload
formData_insert = "      formData.append('modifiers', JSON.stringify(maskModifiers));"
formData_replacement = "      formData.append('modifiers', JSON.stringify(maskModifiers));\n      formData.append('landmark_modifiers', JSON.stringify(landmarkModifiers));"
code = code.replace(formData_insert, formData_replacement)

# 4. Modify the BBox render block to support adjustments
bbox_orig = """                  return (
                    <div 
                      key={face.face_id}
                      className="absolute border-2 border-indigo-500 bg-indigo-500/20 rounded-md transition-all duration-150 pointer-events-none"
                      style={{
                        left: `${(newX1 / mediaSize.width) * 100}%`,
                        top: `${(newY1 / mediaSize.height) * 100}%`,
                        width: `${(newW / mediaSize.width) * 100}%`,
                        height: `${(newH / mediaSize.height) * 100}%`
                      }}
                    >
                      <span className="absolute -top-6 left-0 bg-indigo-600 text-white text-xs font-bold px-1.5 py-0.5 rounded shadow-sm whitespace-nowrap">
                        Face {detectedFaces.findIndex(f => f.face_id === face.face_id) + 1}
                      </span>
                    </div>
                  );"""

bbox_rep = """                  const tmods = landmarkModifiers[face.face_id] || { scale: 1, rotate: 0, x: 0, y: 0 };
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
                  );"""

code = code.replace(bbox_orig, bbox_rep)

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)

print("Patched FaceMappingStudio.tsx for landmark modifiers overlay")
