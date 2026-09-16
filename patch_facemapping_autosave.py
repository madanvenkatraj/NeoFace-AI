import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

# 1. Update targetFile checks
# replace `{!targetFile ? (` with `{!targetPreviewUrl ? (`
code = code.replace("{!targetFile ? (", "{!targetPreviewUrl ? (")
code = code.replace("targetFile.type.startsWith('video')", "isVideo")

# 2. Add handleTargetUpload logic for clearing session when removing target
handle_upload_orig = """  const handleTargetUpload = async (file: File) => {
    setTargetFile(file);
    setTargetPreviewUrl(URL.createObjectURL(file));
    setDetectedFaces([]);
    setFaceMappings({});
    setMaskModifiers({});
    setResultPath(null);
    setJobMetrics(null);
    setJobId(null);
    setError(null);
    setMediaSize(null);
  };"""

handle_upload_rep = """  const handleTargetUpload = async (file: File | null) => {
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
  };"""
code = code.replace(handle_upload_orig, handle_upload_rep)

# Fix onClick for removing target
code = code.replace("onClick={() => handleTargetUpload(null as any)}", "onClick={() => handleTargetUpload(null)}")


# 3. Add auto-save hooks
autosave_hooks = """
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
"""

# Insert hooks right before the keyboard shortcuts hook
code = code.replace("  // Global Keyboard Shortcuts", autosave_hooks + "\n  // Global Keyboard Shortcuts")

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)

print("Patched FaceMappingStudio.tsx for autosave")
