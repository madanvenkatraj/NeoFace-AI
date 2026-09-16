import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    lines = f.readlines()

# find the first occurrence of {sourceSelectionModal && (
first_modal_start = -1
for i, line in enumerate(lines):
    if "{sourceSelectionModal && (" in line:
        first_modal_start = i
        break

if first_modal_start != -1:
    # find where this modal ends. It ends at `      )}` which is line 740.
    modal_end = -1
    for i in range(first_modal_start, len(lines)):
        if "      )}" in lines[i]:
            modal_end = i
            break
            
    if modal_end != -1:
        # Delete from first_modal_start to modal_end inclusive
        del lines[first_modal_start:modal_end+1]

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.writelines(lines)

print("Removed duplicate modal")
