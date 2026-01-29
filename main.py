from flask import Flask, request, send_from_directory
from playwright.sync_api import sync_playwright
import os, time, uuid

app = Flask(__name__)

BASE_DIR = os.getcwd()
VIDEO_DIR = os.path.join(BASE_DIR, "videos")
os.makedirs(VIDEO_DIR, exist_ok=True)

@app.route("/run")
def run():
    url = request.args.get(
        "url",
        "https://www.xataka.com/tag/inteligencia-artificial"
    )

    run_id = str(uuid.uuid4())
    run_video_dir = os.path.join(VIDEO_DIR, run_id)
    os.makedirs(run_video_dir, exist_ok=True)

    articles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir=run_video_dir,
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle")

        # Scroll para cargar más noticias
        for _ in range(6):
            page.mouse.wheel(0, 1500)
            time.sleep(1)

        # Extraer artículos
        items = page.query_selector_all("article h2 a")
        for item in items:
            title = item.inner_text()
            link = item.get_attribute("href")
            articles.append({
                "title": title,
                "url": link
            })

        context.close()
        browser.close()

    return {
        "run_id": run_id,
        "count": len(articles),
        "articles": articles,
        "video": f"/videos/{run_id}"
    }

@app.route("/videos/<path:path>")
def videos(path):
    return send_from_directory("videos", path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
