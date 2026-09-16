import sys

with open("lib/store.ts", "r") as f:
    code = f.read()

code = code.replace(
    "interface WorkspaceState {",
    "interface WorkspaceState {\n  qualityMode?: 'fast' | 'hd';"
)

code = code.replace(
    "  resolution: '1920x1080',",
    "  qualityMode: 'hd',\n  resolution: '1920x1080',"
)

with open("lib/store.ts", "w") as f:
    f.write(code)
print("patched store.ts")
