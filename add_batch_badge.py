with open('app/page.tsx', 'r') as f:
    content = f.read()

badge = """                  <img src={target.previewUrl} alt="Target preview" className="w-full h-full object-cover" />
                )}
                {targets.length > 1 && (
                  <div className="absolute top-4 left-4 bg-indigo-600 shadow-md text-white px-3 py-1.5 rounded-full text-xs font-bold z-50 flex items-center gap-1">
                    <Layers size={14} /> Batch Mode: {targets.length} files
                  </div>
                )}
                <button 
                  onClick={() => setTargets([])}"""

content = content.replace(
"""                  <img src={target.previewUrl} alt="Target preview" className="w-full h-full object-cover" />
                )}
                <button 
                  onClick={() => setTargets([])}""", badge)

with open('app/page.tsx', 'w') as f:
    f.write(content)
