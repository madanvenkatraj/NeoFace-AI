import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

import_insert = "import BeforeAfterPreview from './BeforeAfterPreview';"
import_replacement = "import BeforeAfterPreview from './BeforeAfterPreview';\nimport { auth, db } from '../lib/firebase';\nimport { doc, setDoc } from 'firebase/firestore';"
code = code.replace(import_insert, import_replacement)

keydown_orig = """  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
        e.preventDefault();
        // Undo isn't fully implemented in this older component, but we can reset states
        setFaceMappings({});
        return;
      }

      if (e.key.toLowerCase() === 's') {
        if (targetPath && detectedFaces.length > 0 && !jobId) {
          e.preventDefault();
          startSwap();
        }
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [targetPath, detectedFaces, jobId, faceMappings]);"""

keydown_rep = """  // Global Keyboard Shortcuts
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
  }, [targetPath, detectedFaces, jobId, faceMappings, resultPath, isVideo, qualityMode]);"""

code = code.replace(keydown_orig, keydown_rep)

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)

print("Patched FaceMappingStudio.tsx for keyboard shortcuts")
