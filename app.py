from flask import Flask, request
import os
import util
import whatsappservice

app = Flask(__name__)


@app.route("/welcome", methods=["GET"])
def index():
    return "welcome developer", 200


@app.route("/whatsapp", methods=["GET"])
def VerifyToken():
    try:
        accessToken = os.environ.get("VERIFY_TOKEN")  # desde Railway
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token is not None and challenge is not None and token == accessToken:
            return challenge, 200
        else:
            return "", 400
    except Exception as e:
        print(e)
        return "", 400


@app.route("/whatsapp", methods=["POST"])
def ReceivedMessage():
    try:
        body = request.get_json()
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        message = value["messages"][0]
        number = message["from"]

        text = util.GetTextUser(message)
        GenerateMessage(text, number)
        print(text)

        return "EVENT_RECEIVED", 200
    except Exception as e:
        print(e)
        return "EVENT_RECEIVED", 200


def GenerateMessage(text, number):
    if "text" in text:
        data = util.TextMessage("Text", number)
    elif "format" in text:
        data = util.TextFormatMessage(number)
    elif "image" in text:
        data = util.ImageMessage(number)
    elif "video" in text:
        data = util.VideoMessage(number)
    elif "audio" in text:
        data = util.AudioMessage(number)
    elif "document" in text:
        data = util.DocumentMessage(number)
    elif "location" in text:
        data = util.LocationMessage(number)
    elif "button" in text:
        data = util.ButtonsMessage(number)
    elif "list" in text:
        data = util.ListMessage(number)
    else:
        return

    whatsappservice.SendMessageWhatsapp(data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
