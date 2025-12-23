from flask import Flask, request
import os
import util
import whatsappservice
import time
import threading
import traceback

app = Flask(__name__)

ACCESS_TOKEN = "788BADHHKAIS77"
AGENT_NUMBER = "1234567890"
INACTIVITY_TIMEOUT = 600  # 10 minutos

# { number: { last_time, saludo_enviado, estado } }
active_conversations = {}


def update_conversation(number):
    if number not in active_conversations:
        active_conversations[number] = {
            "last_time": time.time(),
            "saludo_enviado": False,
            "estado": "menu_principal",
        }
    else:
        active_conversations[number]["last_time"] = time.time()


def check_inactive_conversations():
    while True:
        now = time.time()
        for number in list(active_conversations.keys()):
            if now - active_conversations[number]["last_time"] > INACTIVITY_TIMEOUT:
                print(f"Conversación con {number} cerrada por inactividad")
                del active_conversations[number]
        time.sleep(60)


threading.Thread(target=check_inactive_conversations, daemon=True).start()


def notify_agent(number, reason):
    msg = f"Cliente {number} requiere atención: {reason}"
    whatsappservice.SendMessageWhatsapp(util.TextMessage(msg, AGENT_NUMBER))


@app.route("/welcome", methods=["GET"])
def index():
    return "welcome developer", 200


@app.route("/whatsapp", methods=["GET"])
def verify_token():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == ACCESS_TOKEN:
        return challenge
    return "", 400


@app.route("/whatsapp", methods=["POST"])
def received_message():
    try:
        body = request.get_json()

        messages = (
            body.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("messages", [])
        )

        # ⚠️ Evento sin mensaje del usuario → NO RESPONDER
        if not messages:
            return "EVENT_RECEIVED", 200

        message = messages[0]
        number = message.get("from")
        text = util.GetTextUser(message)

        # ⚠️ Texto vacío → NO RESPONDER
        if not number or not text or not text.strip():
            return "EVENT_RECEIVED", 200

        update_conversation(number)
        process_message(text.strip(), number)

        print(f"Mensaje recibido de {number}: {text}")
        return "EVENT_RECEIVED", 200

    except Exception:
        traceback.print_exc()
        return "EVENT_RECEIVED", 500
    
def process_message(text, number):
    convo = active_conversations[number]
    text = text.lower().strip()

    # ---- SALUDO ----
    if not convo["saludo_enviado"]:
        whatsappservice.SendMessageWhatsapp(
            util.TextMessage(
                "¡Hola! 👋 Soy whatsappbot, tu asistente inteligente.\n\n"
                "Elige una opción:\n"
                "1️⃣ Conocer el producto\n"
                "2️⃣ Preguntas frecuentes\n"
                "3️⃣ Hablar con un agente",
                number,
            )
        )
        convo["saludo_enviado"] = True
        return

    # ---- DESPEDIDA ----
    if text in ["ok", "okey", "gracias", "muchas gracias"]:
        whatsappservice.SendMessageWhatsapp(
            util.TextMessage(
                "¡Con gusto! 😊 Que tengas un excelente día 👋",
                number,
            )
        )
        del active_conversations[number]
        return

    # ================= MENÚ PRINCIPAL =================
    if convo["estado"] == "menu_principal":

        if text == "1":
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "🤖 Ofrecemos un servicio adaptado a las necesidades de cada cliente.",
                    number,
                )
            )
            return

        if text == "2":
            convo["estado"] = "faq"
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "📋 Preguntas frecuentes\n\n"
                    "1️⃣ Información general\n"
                    "2️⃣ Cotización personalizada\n"
                    "3️⃣ Volver al menú",
                    number,
                )
            )
            return

        if text == "3":
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "Conectándote con un agente… 🕒",
                    number,
                )
            )
            notify_agent(number, "Hablar con agente")
            return

        # Opción inválida
        whatsappservice.SendMessageWhatsapp(
            util.TextMessage(
                "Selecciona una opción válida:\n"
                "1️⃣ Conocer el producto\n"
                "2️⃣ Preguntas frecuentes\n"
                "3️⃣ Hablar con un agente",
                number,
            )
        )
        return

    # ================= FAQ =================
    if convo["estado"] == "faq":

        if text == "1":
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "ℹ️ Información general\n\n"
                    "El servicio se adapta a tus necesidades.\n"
                    "1️⃣ Nos cuentas qué necesitas\n"
                    "2️⃣ Evaluamos tu caso\n"
                    "3️⃣ Te damos una propuesta personalizada\n\n"
                    "Si deseas una cotización, elige la opción 2️⃣ 😊",
                    number,
                )
            )
            return

        if text == "2" or "precio" in text or "cotiz" in text:
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "🧾 Cotización personalizada\n\n"
                    "Cuéntanos qué necesitas y para cuándo 😊",
                    number,
                )
            )
            notify_agent(number, "Cotización")
            return

        if text == "3":
            convo["estado"] = "menu_principal"
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "Perfecto 👍 Volvemos al menú principal:\n\n"
                    "1️⃣ Conocer el producto\n"
                    "2️⃣ Preguntas frecuentes\n"
                    "3️⃣ Hablar con un agente",
                    number,
                )
            )
            return

        # Opción inválida en FAQ
        whatsappservice.SendMessageWhatsapp(
            util.TextMessage(
                "Elige una opción válida:\n"
                "1️⃣ Información general\n"
                "2️⃣ Cotización personalizada\n"
                "3️⃣ Volver al menú",
                number,
            )
        )
        return




    for msg in responses:
    whatsappservice.SendMessageWhatsapp(msg)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
