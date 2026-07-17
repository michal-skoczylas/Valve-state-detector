from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import cv2
import os
import io
import numpy as np
import json
import threading
import time

app = Flask(__name__)
CORS(app)
IMAGE_FOLDER = 'images'
CONFIG_FOLDER = 'configs'

for folder in [IMAGE_FOLDER, CONFIG_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def get_available_cameras():
    print("Skanowanie podłączonych kamer (to potrwa sekundę)...")
    working_cams = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                working_cams.append(i)
        cap.release()
    print(f"Znaleziono kamery na portach: {working_cams}")
    return working_cams

AVAILABLE_CAMERAS = get_available_cameras()

latest_frame = None
frame_lock = threading.Lock()
active_camera_index = None
cam_state = {
    'h': 0, 's': 0, 'v': 0, 'tol': 20, 'morph': 0, 
    'morph_on': False, 'min_fill': 5, 'rois': []
}

def capture_thread():
    global latest_frame, active_camera_index
    cap = None
    current_idx = None
    
    while True:
        if active_camera_index != current_idx:
            if cap is not None: cap.release()
            if active_camera_index is not None: cap = cv2.VideoCapture(active_camera_index)
            current_idx = active_camera_index
            with frame_lock: latest_frame = None

        if cap is not None and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                with frame_lock: latest_frame = frame.copy()
        else:
            time.sleep(0.1)
        time.sleep(0.03)

threading.Thread(target=capture_thread, daemon=True).start()

@app.route('/refresh_cameras', methods=['GET'])
def refresh_cameras():
    global AVAILABLE_CAMERAS
    AVAILABLE_CAMERAS = get_available_cameras()
    return jsonify(AVAILABLE_CAMERAS)

@app.route('/set_camera/<int:cam_id>', methods=['POST'])
def set_camera(cam_id):
    global active_camera_index
    active_camera_index = cam_id if cam_id >= 0 else None
    return jsonify(success=True)

@app.route('/update_cam_params', methods=['POST'])
def update_cam_params():
    global cam_state
    cam_state.update(request.json)
    return jsonify(success=True)

def gen_original():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is None: continue
            frame = latest_frame.copy()
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.05)

def gen_threshold():
    global latest_frame, cam_state
    while True:
        with frame_lock:
            if latest_frame is None: continue
            frame = latest_frame.copy()
            
        h, tol, morph = cam_state.get('h', 0), cam_state.get('tol', 15), cam_state.get('morph', 0)
        morph_on, rois = cam_state.get('morph_on', False), cam_state.get('rois', [])
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        
        if h > 0 and len(rois) > 0:
            hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_bound = np.array([max(0, h - tol), 40, 40])
            upper_bound = np.array([min(179, h + tol), 255, 255])
            
            for r in rois:
                rx, ry, rw, rh = r.get('rx', 0), r.get('ry', 0), r.get('rw', 0), r.get('rh', 0)
                if rw > 0 and rh > 0 and ry+rh <= frame.shape[0] and rx+rw <= frame.shape[1]:
                    roi_mask = cv2.inRange(hsv_img[ry:ry+rh, rx:rx+rw], lower_bound, upper_bound)
                    if morph_on and morph > 0:
                        k = np.ones((morph if morph % 2 != 0 else morph + 1,)*2, np.uint8)
                        roi_mask = cv2.morphologyEx(cv2.morphologyEx(roi_mask, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
                    mask[ry:ry+rh, rx:rx+rw] = np.maximum(mask[ry:ry+rh, rx:rx+rw], roi_mask)

        ret, buffer = cv2.imencode('.jpg', mask)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.05)

@app.route('/video_original')
def video_original(): return Response(gen_original(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_threshold')
def video_threshold(): return Response(gen_threshold(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_pixel_value')
def camera_pixel_value():
    global latest_frame
    x, y = int(request.args.get('x', 0)), int(request.args.get('y', 0))
    with frame_lock:
        if latest_frame is None: return jsonify({'h': 0, 's': 0, 'v': 0})
        frame = latest_frame.copy()
    if y < 0 or y >= frame.shape[0] or x < 0 or x >= frame.shape[1]: return jsonify({'h': 0, 's': 0, 'v': 0})
    hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    pixel = hsv_img[y, x]
    return jsonify({'h': int(pixel[0]), 's': int(pixel[1]), 'v': int(pixel[2])})

@app.route('/camera_analyze')
def camera_analyze():
    global latest_frame, cam_state
    results = []
    with frame_lock:
        if latest_frame is None: return jsonify(results)
        frame = latest_frame.copy()

    h, tol, morph = cam_state.get('h', 0), cam_state.get('tol', 15), cam_state.get('morph', 0)
    morph_on, min_fill, rois = cam_state.get('morph_on', False), cam_state.get('min_fill', 5.0), cam_state.get('rois', [])
    
    if h > 0 and len(rois) > 0:
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_bound = np.array([max(0, h - tol), 40, 40])
        upper_bound = np.array([min(179, h + tol), 255, 255])
        
        for idx, r in enumerate(rois):
            rx, ry, rw, rh = r.get('rx', 0), r.get('ry', 0), r.get('rw', 0), r.get('rh', 0)
            base_state = r.get('baseState', 'yellow_is_open')
            name = r.get('name', f'ZAWÓR {idx+1}')
            desc = r.get('desc', '')

            if rw > 0 and rh > 0 and ry+rh <= frame.shape[0] and rx+rw <= frame.shape[1]:
                roi_mask = cv2.inRange(hsv_img[ry:ry+rh, rx:rx+rw], lower_bound, upper_bound)
                if morph_on and morph > 0:
                    k = np.ones((morph if morph % 2 != 0 else morph + 1,)*2, np.uint8)
                    roi_mask = cv2.morphologyEx(cv2.morphologyEx(roi_mask, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
                fill_percentage = (cv2.countNonZero(roi_mask) / (rw * rh)) * 100
                
                # --- NOWA LOGIKA STANÓW ---
                is_detected = fill_percentage >= min_fill
                if base_state == 'yellow_is_open':
                    state = "Otwarty" if is_detected else "Zamknięty"
                else:
                    state = "Zamknięty" if is_detected else "Otwarty"
                
                results.append({
                    "id": idx, "name": name, "desc": desc, 
                    "state": state, "fill": round(fill_percentage, 1)
                })
    return jsonify(results)

def get_image_list():
    valid_ext = ('.jpg', '.jpeg', '.png', '.bmp')
    return sorted([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(valid_ext)])

@app.route('/api/init')
def api_init(): return jsonify({"images": get_image_list(), "cameras": AVAILABLE_CAMERAS})

@app.route('/image/<filename>')
def get_original_image(filename): return send_file(os.path.join(IMAGE_FOLDER, filename))

@app.route('/pixel_value/<filename>')
def get_pixel_value(filename):
    x, y = int(request.args.get('x', 0)), int(request.args.get('y', 0))
    img = cv2.imread(os.path.join(IMAGE_FOLDER, filename))
    if img is None: return jsonify({'h': 0, 's': 0, 'v': 0})
    if y < 0 or y >= img.shape[0] or x < 0 or x >= img.shape[1]: return jsonify({'h': 0, 's': 0, 'v': 0})
    pixel = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[y, x]
    return jsonify({'h': int(pixel[0]), 's': int(pixel[1]), 'v': int(pixel[2])})

@app.route('/threshold/<filename>')
def get_threshold_image(filename):
    h, tol, morph = int(request.args.get('h',0)), int(request.args.get('tol',15)), int(request.args.get('morph',0))
    morph_on = request.args.get('morph_on', 'false') == 'true'
    rois = json.loads(request.args.get('rois', '[]'))
    
    img = cv2.imread(os.path.join(IMAGE_FOLDER, filename))
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    if h > 0 and len(rois) > 0:
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_bound = np.array([max(0, h - tol), 40, 40])
        upper_bound = np.array([min(179, h + tol), 255, 255])
        for r in rois:
            rx, ry, rw, rh = r.get('rx', 0), r.get('ry', 0), r.get('rw', 0), r.get('rh', 0)
            if rw > 0 and rh > 0 and ry+rh <= img.shape[0] and rx+rw <= img.shape[1]:
                roi_mask = cv2.inRange(hsv_img[ry:ry+rh, rx:rx+rw], lower_bound, upper_bound)
                if morph_on and morph > 0:
                    k = np.ones((morph if morph%2!=0 else morph+1,)*2, np.uint8)
                    roi_mask = cv2.morphologyEx(cv2.morphologyEx(roi_mask, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
                mask[ry:ry+rh, rx:rx+rw] = np.maximum(mask[ry:ry+rh, rx:rx+rw], roi_mask)
    _, buffer = cv2.imencode(".jpg", mask)
    return send_file(io.BytesIO(buffer), mimetype='image/jpeg')

@app.route('/analyze_valves/<filename>')
def analyze_valves(filename):
    h, tol, morph = int(request.args.get('h',0)), int(request.args.get('tol',15)), int(request.args.get('morph',0))
    morph_on = request.args.get('morph_on', 'false') == 'true'
    min_fill = float(request.args.get('min_fill', 5.0))
    rois = json.loads(request.args.get('rois', '[]'))
    
    img = cv2.imread(os.path.join(IMAGE_FOLDER, filename))
    results = []
    if img is not None and h > 0 and len(rois) > 0:
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_bound = np.array([max(0, h - tol), 40, 40])
        upper_bound = np.array([min(179, h + tol), 255, 255])
        for idx, r in enumerate(rois):
            rx, ry, rw, rh = r.get('rx', 0), r.get('ry', 0), r.get('rw', 0), r.get('rh', 0)
            base_state = r.get('baseState', 'yellow_is_open')
            name = r.get('name', f'ZAWÓR {idx+1}')
            desc = r.get('desc', '')

            if rw > 0 and rh > 0 and ry+rh <= img.shape[0] and rx+rw <= img.shape[1]:
                roi_mask = cv2.inRange(hsv_img[ry:ry+rh, rx:rx+rw], lower_bound, upper_bound)
                if morph_on and morph > 0:
                    k = np.ones((morph if morph%2!=0 else morph+1,)*2, np.uint8)
                    roi_mask = cv2.morphologyEx(cv2.morphologyEx(roi_mask, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
                
                fill_percentage = (cv2.countNonZero(roi_mask) / (rw * rh)) * 100
                is_detected = fill_percentage >= min_fill
                if base_state == 'yellow_is_open':
                    state = "Otwarty" if is_detected else "Zamknięty"
                else:
                    state = "Zamknięty" if is_detected else "Otwarty"
                
                results.append({
                    "id": idx, "name": name, "desc": desc, 
                    "state": state, "fill": round(fill_percentage, 1)
                })
    return jsonify(results)

@app.route('/configs', methods=['GET'])
def get_configs(): return jsonify([f for f in os.listdir(CONFIG_FOLDER) if f.endswith('.json')])

@app.route('/save_config', methods=['POST'])
def save_config():
    data = request.json
    name = data.get('name', 'default').strip()
    if not name: name = 'default'
    if not name.endswith('.json'): name += '.json'
    with open(os.path.join(CONFIG_FOLDER, name), 'w') as f: json.dump(data, f, indent=4)
    return jsonify({"status": "success", "file": name})

@app.route('/load_config/<name>', methods=['GET'])
def load_config(name):
    if not name.endswith('.json'): name += '.json'
    path = os.path.join(CONFIG_FOLDER, name)
    if os.path.exists(path):
        with open(path, 'r') as f: return jsonify(json.load(f))
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, threaded=True)