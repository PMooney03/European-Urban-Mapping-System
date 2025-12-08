#!/usr/bin/env python3
# Extract CSS and JavaScript from index.html and update it

with open('dashboard/templates/dashboard/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# CSS is already extracted, skip style tag extraction
style_start = None
style_end = None

# Find script tag boundaries (the main script, not external CDN scripts)
script_start = None
script_end = None
for i, line in enumerate(lines):
    if '<script>' in line and 'leaflet' not in line.lower() and 'unpkg' not in line.lower():
        script_start = i  # Include the script tag
    if '</script>' in line and script_start is not None and i > script_start:
        script_end = i + 1  # Include the closing tag
        break

# Extract JavaScript content (lines between script tags, excluding the tags themselves)
if script_start is not None and script_end is not None:
    js_content = ''.join(lines[script_start+1:script_end-1])
    with open('static/js/dashboard.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"Extracted JavaScript: {script_end - script_start - 2} lines")

# Create the new HTML content
new_lines = []
for i, line in enumerate(lines):
    if i == script_start:
        # Replace script block with JS link (using Django static tag)
        new_lines.append('    <script src="{% static \'js/dashboard.js\' %}"></script>\n')
    elif script_start is not None and script_start < i < script_end:
        # Skip the script block content
        continue
    else:
        new_lines.append(line)

# Write the updated HTML
with open('dashboard/templates/dashboard/index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Updated index.html with external CSS and JS links")

