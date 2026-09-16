with open('components/NeoFaceStudio.tsx', 'r') as f:
    content = f.read()
    
target = """                  ))}
                </div>
              </div>"""

replacement = """                  ))}
                </div>
                </div>
              </div>"""

if target in content:
    content = content.replace(target, replacement)
    
with open('components/NeoFaceStudio.tsx', 'w') as f:
    f.write(content)
