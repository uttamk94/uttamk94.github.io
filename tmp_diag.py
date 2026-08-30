import re

with open('scripts/algo_content.py', 'rb') as f:
    raw = f.read()

lines = raw.split(b'\n')

# Find ALL ''' sequences (by byte position) in the region 7700-7920
for i in range(7727, 7917):
    line = lines[i]
    for m in re.finditer(b"'''", line):
        context = line[max(0,m.start()-20):m.end()+20]
        print(f'Line {i+1}, byte col {m.start()}: {context!r}')
