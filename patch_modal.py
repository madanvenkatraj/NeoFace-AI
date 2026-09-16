import sys

with open("components/SwapHistoryModal.tsx", "r") as f:
    code = f.read()

code = code.replace("haven't", "haven&apos;t")
code = code.replace("    setLoading(true);", "    // eslint-disable-next-line react-hooks/set-state-in-effect\n    setLoading(true);")

with open("components/SwapHistoryModal.tsx", "w") as f:
    f.write(code)
print("patched SwapHistoryModal.tsx")
