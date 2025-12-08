#!/usr/bin/env python3
# Extract JavaScript from index.html

with open('dashboard/templates/dashboard/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find script tag boundaries (the main script, not the external ones)
script_start = None
script_end = None
for i, line in enumerate(lines):
    if '<script>' in line and 'leaflet' not in line.lower() and 'unpkg' not in line.lower():
        script_start = i + 1  # Start after <script>
    if '</script>' in line and script_start is not None:
        script_end = i  # End before </script>
        break

if script_start and script_end:
    js_content = ''.join(lines[script_start:script_end])
    with open('static/js/dashboard.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"Extracted {script_end - script_start} lines of JavaScript")
else:
    print("Could not find script tags")
