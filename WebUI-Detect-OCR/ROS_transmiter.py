from websocket import create_connection
import json


#テキストを受け取り、jetsonのros bridgeサーバーにメッセージを送信する
def send_to_rosbridge(text):
    # rosbridgeのURLとポート
    ws_url = "ws://192.168.12.100:9090"
    topic = "/goods_class"
    message_type = "std_msgs/String"

    try:
        # Connect to rosbridge
        ws = create_connection(ws_url)
        
        # Message to publish
        payload = {
            "op": "publish",
            "topic": topic,
            "msg": {
                "data": text
            },
            "type": message_type
        }
        
        # Send message
        ws.send(json.dumps(payload))
        ws.close()
        return True  # Successfully sent the message
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False  # Failed to send the message
