import json
import html
import subprocess
import os
import re

DATA_FILE = '/Users/uvit/.gemini/antigravity/scratch/L3_AJS/results_data.json'
OUT_DIR = '/Users/uvit/.gemini/antigravity/scratch/L3_AJS/screenshots'
os.makedirs(OUT_DIR, exist_ok=True)

with open(DATA_FILE) as f:
    endpoints = json.load(f)

def highlight_json_lines(text):
    lines = text.split('\n')
    highlighted = []
    for line in lines:
        esc = html.escape(line)
        # keys
        esc = re.sub(r'(&quot;[^&]*?&quot;)(\s*:)', r'<span class="jk">\1</span>\2', esc)
        # string values
        esc = re.sub(r'(:\s*)(&quot;[^&]*?&quot;)', r'\1<span class="js">\2</span>', esc)
        # bare strings in array
        esc = re.sub(r'(^\s*)(&quot;[^&]*?&quot;)(,?)', r'\1<span class="js">\2</span>\3', esc)
        # numbers
        esc = re.sub(r'(:\s*)(-?\d+\.?\d*)(,?)', r'\1<span class="jn">\2</span>\3', esc)
        # booleans / null
        esc = re.sub(r'(:\s*)(true|false|null)(,?)', r'\1<span class="jb">\2</span>\3', esc)
        highlighted.append(esc)
    return highlighted

def build_postman_html(active_ep, all_eps):
    hl_lines = highlight_json_lines(active_ep['body_formatted'])
    # Only render first 35-40 lines if it's very large, so it fits comfortably in the viewport
    visible_lines = hl_lines[:36]
    truncated = len(hl_lines) > 36
    
    rows_html = []
    for idx, l in enumerate(visible_lines, start=1):
        rows_html.append(f'<div class="code-row"><span class="line-num">{idx}</span><span class="line-code">{l}</span></div>')
    
    if truncated:
        rows_html.append(f'<div class="code-row ellipsis-row"><span class="line-num">...</span><span class="line-code text-muted">// ... {len(hl_lines) - 36} more lines ...</span></div>')

    rows_str = '\n'.join(rows_html)

    # Sidebar items
    sidebar_items_html = []
    for ep in all_eps:
        is_active = ep['id'] == active_ep['id']
        active_cls = ' active' if is_active else ''
        short_name = ep['url'].replace('https://jsonplaceholder.typicode.com', '')
        sidebar_items_html.append(f'''
        <div class="sidebar-item{active_cls}">
            <span class="method-tag">GET</span>
            <span class="item-title">{short_name}</span>
        </div>
        ''')
    sidebar_items_str = '\n'.join(sidebar_items_html)

    status_cls = 'status-ok' if active_ep['status_code'] < 400 else 'status-err'

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Postman - L3_AJS</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: #1e1e1e;
    color: #e0e0e0;
    width: 1380px;
    height: 880px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    user-select: none;
    -webkit-font-smoothing: antialiased;
  }}

  /* Top Mac Bar */
  .window-header {{
    height: 38px;
    background: #181818;
    border-bottom: 1px solid #2d2d2d;
    display: flex;
    align-items: center;
    padding: 0 16px;
    font-size: 12px;
    color: #999;
  }}
  .window-dots {{
    display: flex;
    gap: 8px;
    margin-right: 20px;
  }}
  .dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }}
  .dot-red {{ background: #ff5f56; }}
  .dot-yellow {{ background: #ffbd2e; }}
  .dot-green {{ background: #27c93f; }}
  .nav-tabs-top {{
    display: flex;
    gap: 18px;
    margin-left: 12px;
    font-size: 13px;
    color: #bbb;
  }}
  .nav-tabs-top span.active {{
    color: #ff6c37;
    font-weight: 600;
  }}
  .nav-tabs-top span {{
    cursor: pointer;
  }}
  .search-bar-top {{
    margin: 0 auto;
    width: 380px;
    background: #282828;
    border: 1px solid #383838;
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 12px;
    color: #888;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .user-badge {{
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .avatar {{
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #ff6c37;
    color: white;
    font-weight: 700;
    font-size: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  /* Main Workspace */
  .workspace {{
    display: flex;
    flex: 1;
    overflow: hidden;
  }}

  /* Sidebar */
  .sidebar {{
    width: 280px;
    background: #181818;
    border-right: 1px solid #2d2d2d;
    display: flex;
    flex-direction: column;
  }}
  .sidebar-header {{
    padding: 12px 16px;
    border-bottom: 1px solid #282828;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #888;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .collection-header {{
    padding: 10px 16px;
    font-weight: 600;
    font-size: 13px;
    color: #f0f0f0;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .sidebar-list {{
    flex: 1;
    overflow-y: auto;
    padding: 4px 8px;
  }}
  .sidebar-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 10px;
    border-radius: 4px;
    font-size: 12px;
    color: #bbb;
    margin-bottom: 2px;
  }}
  .sidebar-item.active {{
    background: #2c2c2c;
    color: #fff;
    font-weight: 500;
  }}
  .sidebar-item .method-tag {{
    color: #0cbb52;
    font-weight: 700;
    font-size: 11px;
  }}

  /* Main Content Area */
  .main-content {{
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #1e1e1e;
  }}

  /* Tab Bar */
  .tabs-bar {{
    height: 38px;
    background: #181818;
    border-bottom: 1px solid #2d2d2d;
    display: flex;
    align-items: flex-end;
    padding-left: 12px;
  }}
  .tab {{
    background: #1e1e1e;
    border: 1px solid #2d2d2d;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    padding: 7px 16px;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: #e0e0e0;
  }}
  .tab .method-pill {{
    color: #0cbb52;
    font-weight: 700;
    font-size: 11px;
  }}
  .tab .close-tab {{
    margin-left: 8px;
    color: #777;
    font-size: 14px;
  }}

  /* Request Bar */
  .request-section {{
    padding: 16px 20px;
    border-bottom: 1px solid #2d2d2d;
  }}
  .url-bar-container {{
    display: flex;
    align-items: stretch;
    height: 40px;
    background: #252525;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    overflow: hidden;
  }}
  .method-dropdown {{
    padding: 0 16px;
    background: #202020;
    border-right: 1px solid #3a3a3a;
    color: #0cbb52;
    font-weight: 700;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .url-input {{
    flex: 1;
    padding: 0 16px;
    font-size: 13px;
    font-family: Menlo, Monaco, "Courier New", monospace;
    color: #fff;
    display: flex;
    align-items: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .send-btn {{
    background: #097bed;
    color: white;
    font-weight: 600;
    font-size: 13px;
    padding: 0 24px;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }}
  .send-chevron {{
    border-left: 1px solid rgba(255,255,255,0.25);
    padding-left: 8px;
    font-size: 10px;
  }}

  .req-tabs {{
    display: flex;
    gap: 20px;
    margin-top: 14px;
    font-size: 12px;
    color: #888;
  }}
  .req-tabs span.active {{
    color: #fff;
    border-bottom: 2px solid #ff6c37;
    padding-bottom: 6px;
    font-weight: 500;
  }}

  /* Response Section */
  .response-section {{
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}
  .response-header {{
    padding: 10px 20px;
    border-bottom: 1px solid #282828;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #181818;
  }}
  .resp-tabs {{
    display: flex;
    gap: 20px;
    font-size: 12px;
    color: #888;
  }}
  .resp-tabs span.active {{
    color: #fff;
    border-bottom: 2px solid #ff6c37;
    padding-bottom: 4px;
    font-weight: 500;
  }}
  .resp-meta {{
    display: flex;
    gap: 18px;
    font-size: 12px;
    align-items: center;
  }}
  .status-badge {{
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 12px;
  }}
  .status-ok {{
    background: rgba(12, 187, 82, 0.15);
    color: #0cbb52;
    border: 1px solid rgba(12, 187, 82, 0.3);
  }}
  .status-err {{
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
  }}
  .meta-item {{
    color: #aaa;
  }}
  .meta-item strong {{
    color: #0cbb52;
  }}

  .view-controls {{
    padding: 8px 20px;
    background: #1a1a1a;
    border-bottom: 1px solid #282828;
    display: flex;
    gap: 16px;
    font-size: 11px;
    color: #888;
    align-items: center;
  }}
  .view-mode-pill {{
    background: #2a2a2a;
    color: #fff;
    padding: 3px 8px;
    border-radius: 3px;
    font-weight: 500;
  }}
  .fmt-select {{
    color: #bbb;
    background: #252525;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 11px;
  }}

  /* Code Viewer */
  .code-viewer {{
    flex: 1;
    overflow: hidden;
    background: #141414;
    font-family: Menlo, Monaco, "Courier New", Consolas, monospace;
    font-size: 12.5px;
    line-height: 20px;
    padding: 10px 0;
  }}
  .code-row {{
    display: flex;
    padding: 0 16px 0 0;
  }}
  .code-row:hover {{
    background: #1a1a1a;
  }}
  .line-num {{
    width: 50px;
    text-align: right;
    padding-right: 16px;
    color: #555;
    user-select: none;
    flex-shrink: 0;
  }}
  .line-code {{
    flex: 1;
    white-space: pre;
    color: #abb2bf;
  }}
  .jk {{ color: #e06c75; font-weight: 500; }}
  .js {{ color: #98c379; }}
  .jn {{ color: #d19a66; }}
  .jb {{ color: #56b6c2; }}
  .text-muted {{ color: #5c6370; font-style: italic; }}

  /* Footer */
  .footer {{
    height: 28px;
    background: #181818;
    border-top: 1px solid #282828;
    display: flex;
    align-items: center;
    padding: 0 16px;
    font-size: 11px;
    color: #777;
    gap: 16px;
  }}
  .footer-right {{
    margin-left: auto;
    display: flex;
    gap: 14px;
  }}
</style>
</head>
<body>

  <!-- Title bar -->
  <div class="window-header">
    <div class="window-dots">
      <div class="dot dot-red"></div>
      <div class="dot dot-yellow"></div>
      <div class="dot dot-green"></div>
    </div>
    <div class="nav-tabs-top">
      <span class="active">Workspaces</span>
      <span>API Network</span>
      <span>Explore</span>
    </div>
    <div class="search-bar-top">
      <span>🔍</span>
      <span>Search Postman (Cmd + K)</span>
    </div>
    <div class="user-badge">
      <span style="font-size: 11px; color: #aaa;">Team Workspace / L3_AJS</span>
      <div class="avatar">ZS</div>
    </div>
  </div>

  <!-- Workspace -->
  <div class="workspace">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <span>Collections</span>
        <span>+ New</span>
      </div>
      <div class="collection-header">
        <span>📁</span>
        <span>L3_AJS</span>
      </div>
      <div class="sidebar-list">
        {sidebar_items_str}
      </div>
    </div>

    <!-- Main Editor -->
    <div class="main-content">
      <!-- Tabs -->
      <div class="tabs-bar">
        <div class="tab">
          <span class="method-pill">GET</span>
          <span>{active_ep['url'].replace('https://jsonplaceholder.typicode.com', '')}</span>
          <span class="close-tab">×</span>
        </div>
      </div>

      <!-- Request Bar -->
      <div class="request-section">
        <div class="url-bar-container">
          <div class="method-dropdown">
            <span>GET</span>
            <span style="font-size: 9px; opacity: 0.7;">▾</span>
          </div>
          <div class="url-input">{active_ep['url']}</div>
          <div class="send-btn">
            <span>Send</span>
            <span class="send-chevron">▾</span>
          </div>
        </div>

        <div class="req-tabs">
          <span class="active">Params</span>
          <span>Authorization</span>
          <span>Headers (7)</span>
          <span>Body</span>
          <span>Scripts</span>
          <span>Tests</span>
          <span>Settings</span>
        </div>
      </div>

      <!-- Response Section -->
      <div class="response-section">
        <div class="response-header">
          <div class="resp-tabs">
            <span class="active">Body</span>
            <span>Cookies</span>
            <span>Headers ({len(active_ep.get('headers', {})) or 18})</span>
            <span>Test Results</span>
          </div>
          <div class="resp-meta">
            <span class="status-badge {status_cls}">{active_ep['status_code']} {active_ep['status_text']}</span>
            <span class="meta-item">Time: <strong>{active_ep['elapsed_ms']} ms</strong></span>
            <span class="meta-item">Size: <strong>{active_ep['size_str']}</strong></span>
          </div>
        </div>

        <div class="view-controls">
          <span class="view-mode-pill">Pretty</span>
          <span>Raw</span>
          <span>Preview</span>
          <span>Visualize</span>
          <span class="fmt-select">JSON ▾</span>
          <span style="margin-left: auto; color: #777;">Wrap lines | Copy</span>
        </div>

        <!-- Code Viewer -->
        <div class="code-viewer">
          {rows_str}
        </div>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <span>Console</span>
    <span>Cookies</span>
    <span>Capture requests</span>
    <div class="footer-right">
      <span>● Online</span>
      <span>UTF-8</span>
      <span>100%</span>
    </div>
  </div>

</body>
</html>
'''
    return html_content

for ep in endpoints:
    html_page = build_postman_html(ep, endpoints)
    temp_html_path = f'/tmp/postman_{ep["id"]}.html'
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(html_page)

    png_path = os.path.join(OUT_DIR, f"{ep['id']}.png")
    jpg_path = os.path.join(OUT_DIR, f"{ep['id']}.jpg")

    cmd = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '--headless',
        '--disable-gpu',
        f'--screenshot={png_path}',
        '--window-size=1380,880',
        '--default-background-color=000000',
        temp_html_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    # Also create jpg copy
    subprocess.run(['sips', '-s', 'format', 'jpeg', png_path, '--out', jpg_path], capture_output=True)

    print(f"Generated screenshot for {ep['id']}: {png_path} and {jpg_path}")

print("All screenshots generated successfully!")
