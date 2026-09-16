import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

# Remove the incorrectly appended formData lines
code = code.replace("      formData.append('modifiers', JSON.stringify(modifiersDict));\n", "")
code = code.replace("      formData.append('source_bboxes', JSON.stringify(sourceBboxesDict));\n", "")

orig_mapping = """      formData.append('mapping_data', JSON.stringify({
        mapping: mappingDict,
        embeddings: embeddingsDict,
        modifiers: modifiersDict
      }));"""

new_mapping = """      formData.append('mapping_data', JSON.stringify({
        mapping: mappingDict,
        embeddings: embeddingsDict,
        modifiers: modifiersDict,
        landmark_modifiers: landmarkModifiers,
        source_bboxes: sourceBboxesDict
      }));"""
code = code.replace(orig_mapping, new_mapping)

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)

print("Fixed mapping data payload")
