from flask import Flask, request, jsonify
import requests
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

# Configuración desde variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8506909920:AAFXrIoiSgvEsPi7oCfM6CJqPeKXcJdsBcc')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '6661524923')

def enviar_foto_telegram(screenshot_bytes, caption=""):
    """Envía una foto a Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    files = {'photo': ('screenshot.png', screenshot_bytes, 'image/png')}
    data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
    
    response = requests.post(url, files=files, data=data)
    return response.json()

@app.route('/', methods=['GET'])
def home():
    """Página de inicio"""
    return jsonify({
        'service': 'Playwright Screenshot Bot',
        'status': 'running',
        'endpoints': {
            '/health': 'Health check',
            '/screenshot': 'POST - Captura y envía screenshot',
            '/test': 'GET - Prueba rápida con YouTube'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'service': 'playwright-telegram'})

@app.route('/test', methods=['GET'])
def test():
    """Prueba rápida con el video de YouTube"""
    url = "https://www.youtube.com/watch?v=T_l4QFCRlAc&list=RDMMcSCRoxEso1E&index=10"
    
    try:
        print(f"🎬 Iniciando captura de: {url}")
        
        with sync_playwright() as p:
            print("🚀 Lanzando navegador...")
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            print("📄 Creando página...")
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            print("🌐 Navegando a YouTube...")
            page.goto(url, timeout=60000, wait_until='networkidle')
            
            print("⏳ Esperando que cargue el video...")
            page.wait_for_timeout(5000)
            
            print("📸 Capturando screenshot...")
            screenshot_bytes = page.screenshot(full_page=False)
            
            browser.close()
            print("✅ Screenshot capturado")
            
            print("📤 Enviando a Telegram...")
            resultado = enviar_foto_telegram(
                screenshot_bytes, 
                f"🎥 Test de Playwright\n\n{url}"
            )
            
            if resultado.get('ok'):
                print("✅ ¡Enviado exitosamente a Telegram!")
                return jsonify({
                    'success': True,
                    'message': 'Screenshot enviado a Telegram',
                    'url': url,
                    'telegram_response': resultado
                })
            else:
                print(f"❌ Error al enviar a Telegram: {resultado}")
                return jsonify({
                    'success': False,
                    'error': 'Error al enviar a Telegram',
                    'telegram_response': resultado
                }), 500
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/screenshot', methods=['POST'])
def screenshot():
    """Endpoint para capturar cualquier URL"""
    data = request.json
    url = data.get('url')
    wait_time = data.get('wait_time', 3)
    
    if not url:
        return jsonify({'error': 'URL requerida'}), 400
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            page.goto(url, timeout=60000)
            page.wait_for_timeout(wait_time * 1000)
            
            screenshot_bytes = page.screenshot(full_page=data.get('full_page', False))
            browser.close()
            
            resultado = enviar_foto_telegram(screenshot_bytes, f"📸 {url}")
            
            return jsonify({
                'success': True,
                'url': url,
                'telegram_response': resultado
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Iniciando Playwright Telegram Bot...")
    print(f"📱 Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"🤖 Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    app.run(host='0.0.0.0', port=5000, debug=True)