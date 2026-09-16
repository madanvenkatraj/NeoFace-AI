with open('components/NeoFaceStudio.tsx', 'r') as f:
    content = f.read()

bad_export = """                  ))}
                </div>
                </div>
              </div>
              
              <div className="pt-2">"""

good_export = """                  ))}
                </div>
              </div>
              
              <div className="pt-2">"""

content = content.replace(bad_export, good_export)

with open('components/NeoFaceStudio.tsx', 'w') as f:
    f.write(content)
