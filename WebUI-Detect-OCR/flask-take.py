from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file, Response, request, session
import cv2
import numpy as np
from ultralytics import YOLO
import json
import tempfile
import pymongo
from websocket import create_connection
from camera_utils import perform_detect, perform_ocr, generate_json
from ROS_transmiter import send_to_rosbridge
import socket

app = Flask(__name__)

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

model = YOLO('/Users/shin/develop/ultralytics/checkpoint/yolov8s.pt')

# カメラステータス
global_status = "waiting"
#generate_frams関数の結果
global_results = {
    'detect_result': None,
    'ocr_result': None
}
# カメラが起動しているかどうかを制御するグローバル変数
camera_active = False


#スマホの画面を撮影し物体検出またはOCRを行う
def generate_frames(): 
    global global_results
    global global_status
    global camera_active
    captured_flag = False

    while True:
        if not camera_active:  # 追加
            continue
        if captured_flag:  # すでにキャプチャが成功していれば、ループを抜ける
            break

        success, frame = camera.read()
        if not success:
            break
        else:
            # Get frame dimensions
            frame_height, frame_width, _ = frame.shape
            # Set the y-coordinates directly based on the 20px offset from top and bottom
            top_left_y = 40
            bottom_right_y = frame_height - 40
            # Calculate the new height
            new_height = bottom_right_y - top_left_y
            # Calculate the new width based on the 9:19.5 aspect ratio
            new_width = int(new_height * (10 / 20))
            # Calculate the new x-coordinates based on the new width
            center_x = frame_width // 2
            top_left_x = center_x - (new_width // 2)
            bottom_right_x = center_x + (new_width // 2)
            # Create an overlay with the same shape as the frame
            overlay = np.zeros_like(frame)
            # Fill the overlay with a dark color (you can adjust the color and the intensity)
            overlay.fill(50)
            # Cut out the rectangle area (make it fully transparent)
            overlay[top_left_y:bottom_right_y, top_left_x:bottom_right_x] = frame[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
            # Merge the overlay with the frame
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            # Draw the rectangle
            cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 255, 0), 2)

            results = model.predict(frame, save=False, classes=[67])
            annotated_frame = results[0].plot()
            yolo_boxes = results[0].boxes.xyxy

            if yolo_boxes is not None:
                if len(yolo_boxes) == 1:#一つのcell phone検出時にだけ停止させる
                    yolo_box = yolo_boxes[0]
                    x1, y1, x2, y2 = map(int, yolo_box[:4])
                    
                    # Check if YOLO box entirely covers the rectangle
                    if (x1 <= top_left_x and x2 >= bottom_right_x) and (y1 <= top_left_y and y2 >= bottom_right_y):
                            # # 上下方向に80px、左右方向に50pxのオフセットを設定
                            vertical_offset = 100
                            horizontal_offset = 30
                            # オフセットを加えて領域をクロップ
                            cropped_frame_offset = frame[top_left_y + vertical_offset : bottom_right_y - vertical_offset, 
                                                top_left_x + horizontal_offset : bottom_right_x - horizontal_offset]

                            #携帯画面の撮影(クロップ後)
                            captured_flag = True
                            cv2.imwrite("./static/image/captured_image.jpg", cropped_frame_offset)
                            #撮影画像に対して物体検出を実行
                            detect_result = perform_detect(cropped_frame_offset)
                            print(detect_result)

                            if detect_result == "No detections":
                                ocr_result = perform_ocr("captured_image.jpg")
                                print()
                                print("*** ocr json result ***")
                                print(ocr_result)
                                global_status = "ocr_success"
                                global_results['ocr_result'] = ocr_result
                            else:
                                global_status = "detect_success"
                                global_results['detect_result'] = detect_result

                            
        # フレームをJPEG形式にエンコード
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  


# MongoDBに接続して商品の価格を取得する関数
def get_product_price(product_name):
    # client = pymongo.MongoClient("mongodb://localhost:27017/")
    client = pymongo.MongoClient("mongodb://192.168.12.100:27017/")
    db = client["supermarketDB"]
    collection = db["products"]
    product_data = collection.find_one({"name": product_name})
    if product_data and "price" in product_data:
        return product_data["price"]
    return None


#ルーティングセクション

# ホームページ
@app.route('/', endpoint='home')
def home():
    return render_template('home.html')


# トップページへ戻る
@app.route('/goto_top')
def goto_top():
    global global_status
    global global_results
    global camera_active
    
    # 状態と結果をリセット
    global_status = "waiting"
    global_results = {
        'detect_result': None,
        'ocr_result': None
    }
    camera_active = False
    # トップページ（または任意のページ）にリダイレクト
    return redirect('/')


# 入力ソース選択画面に戻る
@app.route('/goto_camera')
def goto_camera():
    global global_status
    global global_results
    global camera_active
    
    # 状態と結果をリセット
    global_status = "waiting"
    global_results = {
        'detect_result': None,
        'ocr_result': None
    }
    camera_active = False
    # 入力ソース選択画面にリダイレクト
    return redirect('/select-source/camera/')


#選択画面へ
@app.route('/goto_select_source/', methods =['POST', 'GET'], endpoint='goto_select_source')
def goto_select_source():
    return render_template('select-source.html')


#入力ソース選択画面
@app.route('/select-source/', methods=['GET', 'POST'])
def select_source():
    if request.method == 'POST':
        selected_source = request.form['source']
        #カメラ認識
        if selected_source == 'camera':
            return redirect('/select-source/camera')
        #音声認識

    return render_template('select-source.html')


#カメラ検出画面
@app.route('/select-source/camera/')
def camera_index():
    return render_template('camera-index.html')

#カメラ起動用
@app.route('/control_camera', methods=['POST'])
def control_camera():
    global camera_active
    status = request.json.get('status', '')
    
    if status == 'start':
        camera_active = True
    elif status == 'stop':
        camera_active = False
    
    return jsonify({"status": "ok"})


#ビデオストリーム
@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


#物体検出及びOCRステータス
@app.route('/status')
def status():
    return jsonify({"status": global_status})


#結果を受け取り、物体検出及びOCRの確認画面に遷移するため
@app.route('/results')
def results():
    result_type = request.args.get('type', 'detect')  # クエリパラメータから結果のタイプを取得
    result = global_results.get(f"{result_type}_result", 'No result')  # 一時保存した結果を取得

    # もし検出結果が存在し、それが'detect'の場合に価格を取得
    if result_type == 'detect' and result != 'No result':
        prices = {}
        for item in result.split(", "):  # 検出された各アイテムについて
            price = get_product_price(item)  # 価格を取得
            print(f"Checking item: {item}") #デバッグ
            if price is not None:  # 価格情報が存在すれば
                prices[item] = price  # 価格を保存
                print(f"Available items: {prices.keys()}") #デバッグ

    return render_template(f'{result_type}-confirm.html', result=result, item_prices=prices if result_type == 'detect' else None)


#RASAにjsonテキストを送信、ocr-confirmのボタンクリック時
@app.route('/send_to_port_9999', methods=['POST'])
def send_to_port():
    data = request.json
    ocr_result = data.get('result', '')
    json_str = generate_json(ocr_result)
    # 9999番ポートにテキストデータを送る処理
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", 9999))
            s.sendall(json_str.encode('utf-8'))  # utf-8でエンコードして送信
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "fail"}), 500
    

#ROSBridgeサーバーにjsonを送信するためのエンドポイント
@app.route('/ros_transmit', methods=['POST', 'GET'])
def ros_transmit():
    if request.method == 'POST':
        data = request.json
        item_type = data.get("type", "")
    else:
        item_type = request.args.get('type', '')

    if send_to_rosbridge(item_type):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


#rosbridgeへの送信完了画面
@app.route('/send-ros-complete.html')
def send_ros_complete():
    return render_template('send-ros-complete.html')


#rosbridgeへの送信が失敗した場合
@app.route('/send-ros-fail')
def send_ros_fail():
    return render_template('send-ros-fail.html')

    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)