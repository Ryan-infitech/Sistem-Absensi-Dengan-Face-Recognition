import asyncio
import websockets
import cv2
import base64
import json
import ssl
from datetime import datetime

class FaceRecognitionClient:
    def __init__(self, server_uri, camera_index=0):
        self.server_uri = server_uri
        self.camera_index = camera_index
        self.running = False
        # Inisialisasi face detector OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognized_faces = {}  # Menyimpan info wajah yang terdeteksi {name: info}
    
    def encode_frame(self, frame):
        frame = cv2.resize(frame, (640, 480))
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return base64.b64encode(buffer).decode('utf-8')
    
    def detect_faces(self, frame):
        # Konversi frame ke grayscale untuk deteksi wajah
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Deteksi wajah menggunakan OpenCV
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces
    
    def update_recognitions(self, results, current_faces):
        # Update informasi wajah yang dikenali
        if results:
            for result in results:
                name = result['name']
                confidence = result['confidence']
                # Update atau tambah wajah yang dikenali
                self.recognized_faces[name] = {
                    'name': name,
                    'confidence': confidence,
                    'last_seen': datetime.now()
                }
        
        # Hapus rekognisi yang sudah tidak terlihat selama 3 detik
        current_time = datetime.now()
        self.recognized_faces = {
            name: info for name, info in self.recognized_faces.items()
            if (current_time - info['last_seen']).total_seconds() < 3
        }
    
    def draw_results(self, frame, server_results):
        # Deteksi wajah di frame saat ini
        faces = self.detect_faces(frame)
        
        # Update recognitions berdasarkan hasil server
        self.update_recognitions(server_results, faces)
        
        # Gambar bounding box untuk setiap wajah yang terdeteksi
        for (x, y, w, h) in faces:
            # Gambar kotak di sekitar wajah
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Jika ada wajah yang dikenali, tampilkan informasinya
            if self.recognized_faces:
                # Ambil rekognisi pertama (dalam kasus ini kita asumsikan satu wajah)
                recognition = next(iter(self.recognized_faces.values()))
                
                # Gambar label nama dan confidence
                text = f"{recognition['name']} ({recognition['confidence']:.2f})"
                (text_width, text_height), _ = cv2.getTextSize(
                    text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                
                # Kotak background untuk teks
                cv2.rectangle(
                    frame,
                    (x, y - text_height - 5),
                    (x + text_width, y),
                    (0, 255, 0),
                    -1
                )
                
                # Teks nama dan confidence
                cv2.putText(
                    frame,
                    text,
                    (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1
                )
        
        # Tambahkan timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(
            frame,
            timestamp,
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
        
        return frame
    
    async def process_frames(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            raise Exception("Could not open camera")
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        try:
            async with websockets.connect(
                self.server_uri,
                ssl=ssl._create_unverified_context(),
                ping_interval=None,
                ping_timeout=None
            ) as websocket:
                print(f"Connected to server: {self.server_uri}")
                self.running = True
                
                while self.running:
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to capture frame")
                        break
                    
                    try:
                        frame_base64 = self.encode_frame(frame)
                        await websocket.send(frame_base64)
                        
                        try:
                            response = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=5.0
                            )
                            results = json.loads(response)
                            
                            if isinstance(results, dict) and 'error' in results:
                                print(f"Server error: {results['error']}")
                                frame = self.draw_results(frame, [])
                            else:
                                frame = self.draw_results(frame, results)
                        
                        except asyncio.TimeoutError:
                            print("Timeout waiting for server response")
                            frame = self.draw_results(frame, [])
                        
                        cv2.imshow('Face Recognition', frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            self.running = False
                        
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        print(f"Error processing frame: {e}")
                        continue
                        
        except Exception as e:
            print(f"Connection error: {e}")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("Client stopped")
    
    async def start(self):
        try:
            await self.process_frames()
        except Exception as e:
            print(f"Client error: {e}")

def main():
    server_uri = "wss:// URL TUNNELING NGROK .app"
    client = FaceRecognitionClient(server_uri)
    asyncio.run(client.start())

if __name__ == "__main__":
    main()