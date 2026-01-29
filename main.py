from flask import Flask, jsonify
from playwright.sync_api import sync_playwright
import time
import os

app = Flask(__name__)

@app.route("/run/ai-news")
def run_ai_news():
    os.makedirs("videos", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            record_video_dir="videos/"
        )

        page = context.new_page()

        # Página interactiva (ejemplo)
        page.goto("https://www.theverge.com/ai-artificial-intelligence")

        # Esperar a que cargue contenido dinámico
        page.wait_for_selector("h2", timeout=10000)

        # Scroll lento (para que el video se vea bien)
        for _ in range(5):
            page.mouse.wheel(0, 1200)
            time.sleep(1)

        # Tomar screenshot extra (opcional)
        page.screenshot(path="videos/screenshot.png")

        context.close()  # IMPORTANTE: cierra y guarda el video
        browser.close()

    return jsonify({
        "status": "ok",
        "message": "Video grabado",
        "video_dir": "videos/"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
