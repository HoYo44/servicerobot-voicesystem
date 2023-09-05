from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file, Response, request, session
from ultralytics import YOLO
import cv2
import json
from collections import OrderedDict
import pymongo

app = Flask(__name__)
app.secret_key = "my_secret_key" # セッションを使う場合は必要

camera = cv2.VideoCapture(0)
model = YOLO('/home/hayashi/develop/ultralytics/model_pt/yolov8x.pt') 

single_object_counter = 0  # 単一オブジェクト検出カウンターの初期化
detection_completed = False  # 検出完了フラグの初期化
detected_single_class =""
#price = 0

#画面下部にテキストを表示するための関数
def put_centered_text(frame, text, font_scale, color, thickness):
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    text_x = (frame.shape[1] - text_size[0]) // 2
    text_y = frame.shape[0] - 20  # 20ピクセル上に位置するように調整
    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

#物体検出&描画
def generate_frames():
    while True:
        global detection_completed
        global single_object_counter
        global detected_single_class
        #global price
        success, frame = camera.read()

        if not success:
            break
        else:
            # YOLOで画像を処理
            results = model.predict(frame, save=False, classes=[1, 13, 25, 27, 28, 34, 38, 39, 41, 44, 45, 56, 57, 66, 74])

            # 描画
            annotated_frame = results[0].plot()

            # JSON形式の文字列をPythonのリストに変換、nameキーの取得
            json_str = results[0].tojson()
            json_data = json.loads(json_str)
            all_names = {item["name"] for item in json_data}
            detected_classes = ", ".join(all_names)

            # 画面下部中央にテキストを表示
            put_centered_text(annotated_frame, "Please show me only 1 product", 1, (0, 0, 255), 2)

            if len(all_names) == 1:
                #単一クラス物体の検出が行われた場合
                single_object_counter += 1  # カウンターをインクリメント
                text_to_display = f"Detected class: {detected_classes}"
                cv2.putText(annotated_frame, text_to_display, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                if single_object_counter >= 30:
                    detected_single_class = f"{detected_classes}"
                    detection_completed = True  # 検出完了フラグをセット
                    #break
                    price = get_product_price(detected_single_class)
            elif len(all_names) > 1:
                #複数クラス物体の検出が行われた場合
                single_object_counter = 0
                text_to_display = f"Detected class: {detected_classes}"
                cv2.putText(annotated_frame, text_to_display, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                #何も検出されていない場合
                single_object_counter = 0
                text_to_display = "No object detected"
                cv2.putText(annotated_frame, text_to_display, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            
# MongoDBに接続して商品の価格を取得する関数
def get_product_price(product_name):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["supermarketDB"]
    collection = db["products"]
    product_data = collection.find_one({"name": product_name})
    if product_data and "price" in product_data:
        return product_data["price"]
    return None


# 新しいホームページ
@app.route('/', endpoint='home')
def home():
    return render_template('home.html')


#選択画面へ
@app.route('/goto_select_source/', methods =['POST', 'GET'], endpoint='goto_select_source')
def goto_select_source():
    return render_template('select_source.html')


#入力ソースの選択
@app.route('/select-source/', methods=['POST', 'GET'], endpoint='select-source')
def select_source():
    user_choice = request.form.get('choice')
    if user_choice == 'object_detection':
        session['choice'] = 'object_detection'
        return redirect(url_for('DetectionIndex'))
    # 他の選択肢に対する処理もここに追加できます
    return redirect(url_for('home'))

#物体検出
@app.route('/select-source/detection/')
def DetectionIndex():
    global detection_completed
    if detection_completed:
        return "Detection Completed"
    return render_template('detection-index.html')


#物体検出用ビデオ
@app.route('/select-source/detection/video')
def videos():
    global detection_completed
    if detection_completed:
        return "Detection Completed"
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


#物体検出ステータス確認
@app.route('/select-source/detection/status')
def status():
    global detection_completed
    if detection_completed:
        return "Detection Completed"
    return "Detection Ongoing"


#物体検出：単一クラス物体検出完了後、在庫がある場合
@app.route('/select-source/detection/confirm', methods=['GET', 'POST'])
def confirm_instock():
    global detection_completed
    global single_object_counter
    global detected_single_class
    #global price
    
    # MongoDBから価格を取得
    client = pymongo.MongoClient("mongodb://192.168.12.100:27017/")
    db = client["supermarketDB"]
    collection = db["products"]
    product_data = collection.find_one({"name": detected_single_class})
    
    if product_data and "price" in product_data:
        price = product_data["price"]
        print("Product data from DB:", product_data)
        print("Price:", price)
        template_name = 'detection-confirm-InStock.html'
    else:
        price = "Not available"
        template_name = 'detection-confirm-NoStock.html'

    if request.method == 'POST':
        user_response = request.form.get('confirm')
        if user_response == 'yes':
            detection_completed = True  # 検出を停止
            return "Send goods information to the robot."
        elif user_response == 'again':
            detection_completed = False  # 検出を再開
            single_object_counter = 0  # カウンターをリセット

        return redirect(url_for('DetectionIndex'))

    return render_template(template_name, detected_class = detected_single_class, price=price)



if __name__ == "__main__":
    app.run(debug=False)


