import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

card_sig_orig = "function FaceMappingCard({ face, index, mapping, maskExpansion, maskErosion, onMaskChange, onUpload, onClear }: any) {"
card_sig_new = "function FaceMappingCard({ face, index, mapping, maskExpansion, maskErosion, onMaskChange, onUpload, onClear, isLoading }: any) {"
code = code.replace(card_sig_orig, card_sig_new)

usage_orig = """                mapping={faceMappings[face.face_id]}"""
usage_new = """                mapping={faceMappings[face.face_id]}
                isLoading={sourceModalLoading === face.face_id}"""
code = code.replace(usage_orig, usage_new)

dropzone_orig = """            <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-colors ${isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50'}`}>
              <input {...getInputProps()} />
              <UploadCloud className="mx-auto text-slate-400 mb-2" size={24} />
              <p className="text-sm text-slate-600 font-medium">Upload Source Face</p>
              <p className="text-xs text-slate-400 mt-1">Drag & drop or click</p>
            </div>"""

dropzone_new = """            <div {...getRootProps()} className={`relative border-2 border-dashed rounded-xl p-4 text-center transition-colors ${isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50'} ${isLoading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}`}>
              <input {...getInputProps()} />
              {isLoading ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-50/80 rounded-xl z-10">
                  <Loader2 className="animate-spin text-indigo-500 mb-2" size={24} />
                  <p className="text-sm font-semibold text-slate-700">Analyzing Image...</p>
                </div>
              ) : (
                <>
                  <UploadCloud className="mx-auto text-slate-400 mb-2" size={24} />
                  <p className="text-sm text-slate-600 font-medium">Upload Source Face</p>
                  <p className="text-xs text-slate-400 mt-1">Drag & drop or click</p>
                </>
              )}
            </div>"""
code = code.replace(dropzone_orig, dropzone_new)

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)

print("Patched FaceMappingCard for loading state")
