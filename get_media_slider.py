with open('app/page.tsx', 'r') as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if "const MediaCompareSlider = " in line:
        start_idx = i
        break

if start_idx != -1:
    end_idx = -1
    open_brackets = 0
    for i in range(start_idx, len(lines)):
        open_brackets += lines[i].count('{') - lines[i].count('}')
        if open_brackets == 0 and i > start_idx:
            end_idx = i
            break
    print("".join(lines[start_idx:end_idx+1]))
