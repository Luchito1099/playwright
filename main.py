from flask import Flask, jsonify
import threading
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def run_playwright():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://example.com", timeout=30000)
            title = page.title()
            print("✅ TITLE:", title)
            browser.close()
    except Exception as e:
        print("❌ Playwright error:", e)

@app.route("/run")
def run():
    threading.Thread(target=run_playwright, daemon=True).start()
    return jsonify({"status": "playwright started"}), 200

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
