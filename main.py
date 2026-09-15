from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
import math

app = FastAPI()
# SET base directory here, just map your directory when use docker
BASE_DIR = Path("./logs").resolve()
STATICS_DIR = Path("./statics").resolve()

# Mount the root directory to serve raw media files
app.mount("/files", StaticFiles(directory=str(BASE_DIR)), name="files")
app.mount("/statics", StaticFiles(directory=str(STATICS_DIR)), name="statics")

@app.get("/", response_class=HTMLResponse)
@app.get("/browse/{subpath:path}", response_class=HTMLResponse)
def image_gallery(subpath: str = "", page: int = 1, page_size: int = 24):
    target_dir = (BASE_DIR / subpath).resolve()

    # Security safeguard against path traversal attacks
    if not target_dir.is_relative_to(BASE_DIR) or not target_dir.exists() or not target_dir.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")

    items = sorted(os.listdir(target_dir),reverse=True)
    folders, images = [], []
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp')

    for item in items:
        item_path = target_dir / item
        rel_path = item_path.relative_to(BASE_DIR).as_posix()
        if item_path.is_dir():
            folders.append((item, rel_path))
        elif item.lower().endswith(image_extensions):
            images.append((item, rel_path))

    # Pagination calculation for images
    total_images = len(images)
    total_pages = max(1, math.ceil(total_images / page_size))
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_images = images[start_idx:end_idx]

    # Navigation up link
    back_link = ""
    if subpath:
        parent_path = Path(subpath).parent.as_posix()
        parent_link = "" if parent_path == "." else f"/{parent_path}"
        back_link = f'<a href="/browse{parent_link}" style="display: inline-block; margin-bottom: 15px; text-decoration: none; font-weight: bold; color: #333;">📁 .. (Up one level)</a>'

    folder_html = "".join([
        f'<div style="background: #f4f4f4; padding: 10px 15px; border-radius: 6px; ">'
        f'<a href="/browse/{rel}" style="text-decoration: none; color: #0066cc; font-weight: 500;">📁 {name}</a>'
        f'</div>'
        for name, rel in folders
    ])

    image_html = "".join([
        f'<div style="margin: 10px; display: inline-block; text-align: center; vertical-align: top; cursor: pointer;" onclick="openModal(\'/files/{rel}\', \'{name}\')">'
        f'<img src="/files/{rel}" loading="lazy" style="width: 150px; height: 150px; object-fit: cover; display: block; border-radius: 8px; border: 1px solid #ddd;" />'
        f'<p style="font-size: 12px; max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 5px;" title="{name}">{name}</p>'
        f'</div>'
        for name, rel in paginated_images
    ])

    # Pagination controls HTML
    base_url = f"/browse/{subpath}" if subpath else "/"
    pagination_links = []

    if page > 1:
        pagination_links.append(f'<a href="{base_url}?page={page-1}&page_size={page_size}" style="padding: 6px 14px; background: #0066cc; color: white; border-radius: 4px; text-decoration: none;">Previous</a>')
    else:
        pagination_links.append(f'<span style="padding: 6px 14px; background: #ddd; color: #888; border-radius: 4px;">Previous</span>')

    pagination_links.append(f'<span style="padding: 6px 12px; font-weight: 500;">Page {page} of {total_pages} ({total_images} images)</span>')

    if page < total_pages:
        pagination_links.append(f'<a href="{base_url}?page={page+1}&page_size={page_size}" style="padding: 6px 14px; background: #0066cc; color: white; border-radius: 4px; text-decoration: none;">Next</a>')
    else:
        pagination_links.append(f'<span style="padding: 6px 14px; background: #ddd; color: #888; border-radius: 4px;">Next</span>')

    pagination_html = f'<div style="margin: 20px 0; display: flex; gap: 10px; align-items: center;">{"".join(pagination_links)}</div>'

    return f"""
    <html>
        <head>
            <title>Simple Image Gallery</title>
            <link href="/statics/iconfont/iconfont.css" rel="stylesheet">
            <style>
                #imageModal {{
                    display: none;
                    position: fixed;
                    z-index: 1000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.8);
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                }}
                #modalImg {{
                    max-width: 90%;
                    max-height: 80vh;
                    border-radius: 4px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.5);
                }}
                #modalCaption {{
                    color: white;
                    position: absolute;
                    top: 40px;
                    left: 50%;
                    transform: translateX(-50%);
                    font-size: 16px;
                    position: absolute; 
                    background: rgba(0,0,0,0.5);
                    padding: 5px 15px;
                    border-radius: 4px;
                }}
                #modalAction {{
                    position: absolute;
                    bottom: 40px; 
                    left: 50%;
                    transform: translateX(-50%); 
                    display: flex; 
                    gap: 10px; 
                    z-index: 1001;
                    background: rgba(0,0,0,0.5);
                    padding: 5px 15px;
                    border-radius: 4px;
                }}
                #modalAction > button {{
                    border: none;
                    color: white;
                    padding: 8px 12px;
                    background: transparent;
                    font-size: 16px;
                }}
                #modalAction > button > .iconfont {{
                    font-size: 18px
                }}
                .close-btn {{
                    position: absolute;
                    top: 20px;
                    right: 30px;
                    color: #f1f1f1;
                    font-size: 40px;
                    font-weight: bold;
                    cursor: pointer;
                }}
            </style>
        </head>
        <body style="font-family: sans-serif; padding: 20px; color: #333; max-width: 1200px; margin: auto;">
            <h2>Current Directory: /{subpath}</h2>
            {back_link}
            <h3>Folders</h3>
            <div style="display: flex; flex-wrap: wrap; flex-direction: row; gap: 8px;">{folder_html if folder_html else '<p style="color: gray; font-size: 14px;">No subfolders</p>'}</div>
            <hr style="margin: 20px 0; border: 0; border-top: 1px solid #eee;"/>
            <h3>Images</h3>
            {pagination_html if total_images > 0 else ''}
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">{image_html if image_html else '<p style="color: gray; font-size: 14px;">No images here</p>'}</div>
            {pagination_html if total_images > 0 else ''}

            <!-- Modal Viewer Dialog -->
            <div id="imageModal" onclick="if(event.target === this) closeModal()">
                <span class="close-btn" onclick="closeModal()">&times;</span>
                <div id="modalCaption"></div>
                <div style="overflow: hidden; display: flex; justify-content: center; align-items: center; width: 100%; height: 100%;">
                    <img id="modalImg" style="transition: transform 0.1s ease; transform-origin: center; cursor: grab;" />
                </div>
                <div id="modalAction">
                    <button onclick="rotateImage(90)"><i class="iconfont ig-rotateright"></i></button>
                    <button onclick="rotateImage(-90)"><i class="iconfont ig-rotateleft"></i></button>
                    <button onclick="zoomIn()"><i class="iconfont ig-zoomin"></i></button>
                    <button onclick="zoomOut()"><i class="iconfont ig-zoomout"></i></button>
                    <button onclick="resetZoomRotate()"><i class="iconfont ig-reset"></i></button>
                </div>
            </div>

            <script>
                let currentScale = 1;
                let currentRotation = 0;

                function openModal(src, caption) {{
                    currentScale = 1;
                    currentRotation = 0;
                    let img = document.getElementById('modalImg');
                    img.src = src;
                    updateTransform();
                    document.getElementById('modalCaption').innerText = caption;
                    document.getElementById('imageModal').style.display = 'flex';
                }}

                function closeModal() {{
                    document.getElementById('imageModal').style.display = 'none';
                }}

                function rotateImage(deg) {{
                    currentRotation = (currentRotation + deg) % 360;
                    updateTransform();
                }}

                function resetZoomRotate() {{
                    currentScale = 1;
                    currentRotation = 0;
                    updateTransform();
                }}

                function zoomIn() {{
                    currentScale += 0.1
                    updateTransform();
                }}

                function zoomOut() {{
                    currentScale = Math.max(0.2, currentScale - 0.1);
                    updateTransform();
                }}

                function updateTransform() {{
                    let img = document.getElementById('modalImg');
                    img.style.transform = `scale(${{currentScale}}) rotate(${{currentRotation}}deg)`;
                }}

                // Zoom with Mouse Wheel
                document.getElementById('imageModal').addEventListener('wheel', function(event) {{
                    event.preventDefault();
                    if (event.deltaY < 0) {{
                        currentScale += 0.1; // Zoom in
                    }} else {{
                        currentScale = Math.max(0.2, currentScale - 0.1); // Zoom out
                    }}
                    updateTransform();
                }}, {{ passive: false }});

                // Close on ESC key press
                document.addEventListener('keydown', function(event) {{
                    if (event.key === "Escape") {{
                        closeModal();
                    }}
                }});
            </script>
        </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)