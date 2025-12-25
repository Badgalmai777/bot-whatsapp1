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


# ================= UTILIDADES =================

def update_conversation(number):
    if number not in active_conversations:
        active_conversations[number] = {
            "last_time": time.time(),
            "saludo_enviado": False,
            "estado": "menu_principal",
        }
    else:
        active_conversations[number]["last_time"] = time.time()


def close_conversation(number):
    if number in active_conversations:
        del active_conversations[number]


def check_inactive_conversations():
    while True:
        now = time.time()
        for number in list(active_conversations.keys()):
            if now - active_conversations[number]["last_time"] > INACTIVITY_TIMEOUT:
                print(f"Conversación con {number} cerrada por inactividad")
                close_conversation(number)
        time.sleep(60)


threading.Thread(target=check_inactive_conversations, daemon=True).start()


def notify_agent(number, reason):
    msg = f"📞 Cliente {number} requiere atención: {reason}"
    whatsappservice.SendMessageWhatsapp(
        util.TextMessage(msg, AGENT_NUMBER)
    )


# ================= RUTAS =================

@app.route("/welcome", methods=["GET"])
def index():
    return "welcome developer", 200


@app.route("/whatsapp", methods=["GET"])
def verify_token():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == ACCESS_TOKEN:
        return challenge, 200
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

        if not messages:
            return "EVENT_RECEIVED", 200

        message = messages[0]
        number = message.get("from")
        text = util.GetTextUser(message)

        if not number or not text:
            return "EVENT_RECEIVED", 200

        update_conversation(number)
        process_message(text, number)

        print(f"Mensaje recibido de {number}: {text}")
        return "EVENT_RECEIVED", 200

    except Exception:
        traceback.print_exc()
        return "EVENT_RECEIVED", 500


# ================= LÓGICA DEL BOT =================

def process_message(text, number):
    convo = active_conversations[number]
    text = (text or "").lower().strip()

    # ---- SALUDO INICIAL ----
    if not convo["saludo_enviado"]:
        whatsappservice.SendMessageWhatsapp(
            util.TextMessage(
                "¡Hola! 👋 Soy whatsappbot, tu asistente inteligente.\n\n"
                "Elige una opción:\n"
                "1️⃣ Conocer el producto\n"
                "2️⃣ Cotización personalizada\n"
                "3️⃣ Hablar con un agente",
                number,
            )
        )
        convo["saludo_enviado"] = True
        convo["estado"] = "menu_principal"
        convo["confirmacion_enviada"] = False
        convo["origen"] = None
        return

    # ---- ESPERANDO AGENTE ----
    if convo["estado"] == "esperando_agente":

        # 🔁 Volver al menú
        if text in ["menu", "inicio", "volver"]:
            convo["estado"] = "menu_principal"
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "🔙 Menú principal:\n\n"
                    "1️⃣ Conocer el producto\n"
                    "2️⃣ Cotización personalizada\n"
                    "3️⃣ Hablar con un agente",
                    number,
                )
            )
            return

        # ✅ CONFIRMACIÓN SOLO PARA COTIZACIÓN
        if (
            convo.get("origen") == "cotizacion"
            and not convo.get("confirmacion_enviada")
        ):
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "Perfecto 😊 te contactaremos a lo largo del día.\n\n"
                    "Si deseas volver al menú principal, escribe *menu*.",
                    number,
                )
            )
            convo["confirmacion_enviada"] = True
            return

        # 🔕 Silencio total
        return

    # ---- DESPEDIDA ----
    if text in ["ok", "okey", "gracias", "muchas gracias"]:
        whatsappservice.SendMessageWhatsapp(
            util.TextMessage(
                "¡Con gusto! 😊 Que tengas un excelente día 👋",
                number,
            )
        )
        close_conversation(number)
        return

    # ---- MENÚ PRINCIPAL ----
    if convo["estado"] == "menu_principal":

        if text == "1":
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "🤖 Ofrecemos un servicio adaptado a las necesidades de cada cliente.\n"
                    "Automatizamos procesos y brindamos atención eficiente 😊",
                    number,
                )
            )
            return

        elif text == "2" or ("precio" in text) or ("cotiz" in text):
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "🧾 Cotización personalizada\n\n"
                    "Cuéntanos brevemente:\n"
                    "• Qué necesitas\n"
                    "• Para cuándo lo necesitas\n\n"
                    "Un agente te responderá pronto 😊",
                    number,
                )
            )
            notify_agent(number, "Cotización")
            convo["estado"] = "esperando_agente"
            convo["confirmacion_enviada"] = False
            convo["origen"] = "cotizacion"
            return

        elif text == "3":
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "📞 Te conectamos con un agente, un momento por favor…",
                    number,
                )
            )
            notify_agent(number, "Hablar con agente")
            convo["estado"] = "esperando_agente"
            convo["confirmacion_enviada"] = False
            convo["origen"] = "agente"
            return

        else:
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "❗ Opción no válida.\n\n"
                    "1️⃣ Conocer el producto\n"
                    "2️⃣ Cotización personalizada\n"
                    "3️⃣ Hablar con un agente",
                    number,
                )
            )
            return



# ================= MAIN =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


