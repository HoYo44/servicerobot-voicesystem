from ultralytics import YOLO
import cv2
import json
import numpy as np
from PIL import Image
import pytesseract
import re
# from googletrans import Translator

model = YOLO('/Users/shin/develop/ultralytics/checkpoint/yolov8s.pt')  # モデルのパスを指定


#物体検出
def perform_detect(image):
    results = model.predict(image, save=False, classes=[1, 13, 25, 27, 28, 34, 38, 39, 41, 44, 45, 56, 57, 66, 74])
    annotated_image = results[0].plot()

    json_str = results[0].tojson()
    json_data = json.loads(json_str)
    all_names = {item["name"] for item in json_data}

    if len(all_names) == 0:  # 何も検出されなかった場合
        return "No detections"
    else:
        annotated_image = results[0].plot()
        cv2.imwrite("./static/image/annotated_image.jpg", annotated_image)
        detected_classes = ", ".join(all_names)
        return detected_classes


#OCR
def perform_ocr(image_path):
    #cv2によるOCRのための画像処理
    img_cv = cv2.imread(image_path) # OpenCVで画像を読み込む
    # グレースケール変換
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    # 二値化
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # 輪郭を検出
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # OCRを適用
    text = pytesseract.image_to_string(Image.fromarray(img_cv), lang='eng')
    text = text.replace('\n', ' ')  # 改行をスペースに置き換え
    json_text = generate_json(text)
    print(json_text)
    return text
    # Google Translateを使って日本語を英語に翻訳
    # translator = Translator()
    # words = text.split(' ')
    # translated_words = []

    # for word in words:
    #     if re.match(r'[\u3040-\u30FF\u4E00-\u9FFF]+', word):  # 日本語の文字が含まれているかチェック
    #         translated = translator.translate(word, src='jp', dest='en')
    #         translated_words.append(translated.text)
    #     else:
    #         translated_words.append(word)

    # translated_text = ' '.join(translated_words)
    # cleaned_translated_text = re.sub(r"[^a-zA-Z0-9.,']", " ", translated_text)  # アルファベット、ドット、カンマ、数字、シングルクオーテーション以外の文字を削除
    # return cleaned_translated_text


#RASAに渡すためのjson生成関数
def generate_json(ocr_text):
    # ここで指定のデータ構造を作成
    data = [
        {
            'recognized_text': ocr_text
        }
    ]
    # PythonのリストをJSON形式の文字列に変換
    json_str = json.dumps(data, ensure_ascii=False, indent=4)
    return json_str