import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

code = code.replace("  const [sourceModalLoading, setSourceModalLoading] = useState<string | null>(null);", "  const [sourceModalLoading, setSourceModalLoading] = useState<string | null>(null);\n  const [sourceModalSize, setSourceModalSize] = useState<{width: number, height: number} | null>(null);")

code = code.replace("setSourceSelectionModal(null)", "setSourceSelectionModal(null); setSourceModalSize(null)")

img_jsx_orig = """                <img 
                  id="source-modal-img"
                  src={sourceSelectionModal.previewUrl} 
                  alt="Source" 
                  className="max-h-[60vh] max-w-full object-contain block"
                />"""
img_jsx_new = """                <img 
                  id="source-modal-img"
                  src={sourceSelectionModal.previewUrl} 
                  alt="Source" 
                  className="max-h-[60vh] max-w-full object-contain block"
                  onLoad={(e: any) => setSourceModalSize({width: e.target.naturalWidth, height: e.target.naturalHeight})}
                />"""
code = code.replace(img_jsx_orig, img_jsx_new)


bbox_jsx_orig = """                      style={{
                        left: `${(face.bbox[0] / (document.getElementById('source-modal-img') as HTMLImageElement)?.naturalWidth || 1) * 100}%`,
                        top: `${(face.bbox[1] / (document.getElementById('source-modal-img') as HTMLImageElement)?.naturalHeight || 1) * 100}%`,
                        width: `${((face.bbox[2] - face.bbox[0]) / (document.getElementById('source-modal-img') as HTMLImageElement)?.naturalWidth || 1) * 100}%`,
                        height: `${((face.bbox[3] - face.bbox[1]) / (document.getElementById('source-modal-img') as HTMLImageElement)?.naturalHeight || 1) * 100}%`,
                      }}"""
bbox_jsx_new = """                      style={sourceModalSize ? {
                        left: `${(face.bbox[0] / sourceModalSize.width) * 100}%`,
                        top: `${(face.bbox[1] / sourceModalSize.height) * 100}%`,
                        width: `${((face.bbox[2] - face.bbox[0]) / sourceModalSize.width) * 100}%`,
                        height: `${((face.bbox[3] - face.bbox[1]) / sourceModalSize.height) * 100}%`,
                      } : { display: 'none' }}"""
code = code.replace(bbox_jsx_orig, bbox_jsx_new)


with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)

print("Fixed modal dimensions")
