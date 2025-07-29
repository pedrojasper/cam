import cv2
from flask import Flask, Response, render_template
import threading
import webbrowser

app = Flask(__name__)

# Configuración
HOST = '0.0.0.0'  # Escucha en todas las interfaces
PORT = 3000       # Puerto 3000 como solicitaste
AUTOSTART_BROWSER = True  # Abrir navegador automáticamente

# Inicializar la cámara
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Redimensionar y convertir a JPEG
            frame = cv2.resize(frame, (640, 480))
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def run_server():
    app.run(host=HOST, port=PORT, threaded=True)

if __name__ == '__main__':
    # Crear estructura de templates si no existe
    import os
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Crear archivo HTML con estilo moderno
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cámara Web</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            color: #2c3e50;
        }
        .video-container {
            position: relative;
            padding-bottom: 56.25%; /* 16:9 */
            height: 0;
            overflow: hidden;
            margin-bottom: 20px;
            border-radius: 8px;
            background: #000;
        }
        .video-container img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        .status {
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .controls {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            padding: 10px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #2980b9;
        }
        footer {
            text-align: center;
            margin-top: 30px;
            font-size: 12px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Streaming de Cámara Web</h1>
        
        <div class="status">
            <p id="status">Conectando a la cámara...</p>
        </div>
        
        <div class="video-container">
            <img src="{{ url_for('video_feed') }}" alt="Video en vivo" id="video">
        </div>
        
        <div class="controls">
            <button onclick="takeSnapshot()">Tomar Foto</button>
            <button onclick="toggleFullscreen()">Pantalla Completa</button>
        </div>
        
        <footer>
            Servidor de cámara web - Python + Flask + OpenCV
        </footer>
    </div>

    <script>
        const video = document.getElementById('video');
        const status = document.getElementById('status');
        
        video.onload = function() {
            status.textContent = "Cámara conectada correctamente";
        };
        
        video.onerror = function() {
            status.textContent = "Error al conectar con la cámara";
        };
        
        function takeSnapshot() {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth || video.width;
            canvas.height = video.videoHeight || video.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const link = document.createElement('a');
            link.download = 'snapshot-' + new Date().toISOString() + '.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        }
        
        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                video.requestFullscreen().catch(err => {
                    alert(`Error al intentar pantalla completa: ${err.message}`);
                });
            } else {
                document.exitFullscreen();
            }
        }
    </script>
</body>
</html>
        ''')
    
    # Iniciar el servidor en un hilo separado
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Abrir navegador automáticamente
    if AUTOSTART_BROWSER:
        webbrowser.open(f'http://localhost:{PORT}')
    
    # Mantener el script corriendo
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
        camera.release()
