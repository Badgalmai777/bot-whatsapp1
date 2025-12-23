from flask import Flask, request
import os
import util
import whatsappservice
import time
import threading
import traceback

app = Flask(__name__)

ACCESS_TOKEN = "788BADHHKAIS77"
AGENT_NUMBER = "1234567890"  # Número del agente que recibirá notificaciones
INACTIVITY_TIMEOUT = 600  # 10 minutos

# Diccionario para conversaciones activas {number: {"last_time": timestamp, "saludo_enviado": bool}}
active_conversations = {}


# Función para actualizar timestamp de la conversación
def update_conversation(number):
    if number in active_conversations:
        active_conversations[number]["last_time"] = time.time()
    else:
        active_conversations[number] = {
            "last_time": time.time(),
            "saludo_enviado": False,
        }


def check_inactive_conversations():
    while True:
        now = time.time()
        inactive = []
        for number, data in list(active_conversations.items()):
            if now - data["last_time"] > INACTIVITY_TIMEOUT:
                inactive.append(number)

        for number in inactive:
            print(f"Conversación con {number} terminada por inactividad")
            # ❌ NO enviar mensajes
            del active_conversations[number]

        time.sleep(60)


# Inicia el hilo de revisión de inactividad
threading.Thread(target=check_inactive_conversations, daemon=True).start()


# Notificar al agente
def notify_agent(number, reason):
    message = f"Cliente {number} requiere atención: {reason}"
    whatsappservice.SendMessageWhatsapp(util.TextMessage(message, AGENT_NUMBER))


# Ruta de prueba
@app.route("/welcome", methods=["GET"])
def index():
    return "welcome developer", 200


# Verificación del token de WhatsApp
@app.route("/whatsapp", methods=["GET"])
def verify_token():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token and challenge and token == ACCESS_TOKEN:
        return challenge
    return "", 400


# Recepción de mensajes
@app.route("/whatsapp", methods=["POST"])
def received_message():
    try:
        body = request.get_json()
        entry = body.get("entry", [])
        if not entry:
            return "No entry", 400
        changes = entry[0].get("changes", [])
        if not changes:
            return "No changes", 400
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return "No messages", 200  # No es error, puede ser evento de estado

        message = messages[0]
        number = message.get("from")
        text = util.GetTextUser(message)

        if not number or not text:
            return "Invalid message", 400

        # Actualiza la conversación activa
        update_conversation(number)
        process_message(text, number)

        print(f"Mensaje recibido: {text} de {number}")
        return "EVENT_RECEIVED", 200
    except Exception:
        print("Error procesando mensaje:")
        traceback.print_exc()
        return "EVENT_RECEIVED", 500


def process_message(text, number):
    # Inicializar conversación si no existe
    if number not in active_conversations:
        active_conversations[number] = {
            "saludo_enviado": False,
            "estado": "menu_principal",  # menu_principal | faq
        }

    # ---- SALUDO INICIAL ----
    if not active_conversations[number]["saludo_enviado"]:
        whatsappservice.SendMessageWhatsapp(
            util.TextMessage(
                "¡Hola! 👋 Soy whatsappbot, tu asistente inteligente.\n\n"
                "Por favor, elige una opción:\n"
                "1️⃣ Conocer el producto\n"
                "2️⃣ Preguntas frecuentes\n"
                "3️⃣ Hablar con un agente",
                number,
            )
        )
        active_conversations[number]["saludo_enviado"] = True
        return

    # Si no hay texto
    if not text or text.strip() == "":
        return

    text = text.lower().strip()
    estado = active_conversations[number]["estado"]

    # ---- DESPEDIDA ----
    if text in ["ok", "okey", "gracias", "gracias!", "muchas gracias"]:
        whatsappservice.SendMessageWhatsapp(
            util.TextMessage(
                "¡Con gusto! 😊 Ha sido un placer ayudarte.\n"
                "¡Que tengas un excelente día! 👋",
                number,
            )
        )
        active_conversations.pop(number, None)
        return

    # ================= MENÚ PRINCIPAL =================
    if estado == "menu_principal":

        if text == "1":
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "🤖 Ofrecemos un servicio adaptado a las necesidades de cada cliente.\n"
                    "Automatizamos procesos y brindamos atención eficiente 😊",
                    number,
                )
            )

        elif text == "2":
            active_conversations[number]["estado"] = "faq"
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "📋 Preguntas frecuentes\n\n"
                    "1️⃣ Información general\n"
                    "2️⃣ Cotización personalizada\n"
                    "3️⃣ Volver al menú",
                    number,
                )
            )

        elif text == "3":
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "Conectándote con un agente humano… un momento por favor 🕒",
                    number,
                )
            )
            notify_agent(number, "Solicitud de agente")

        else:
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "Opción no válida 😕\n\n"
                    "1️⃣ Conocer el producto\n"
                    "2️⃣ Preguntas frecuentes\n"
                    "3️⃣ Hablar con un agente",
                    number,
                )
            )

    # ================= FAQ =================
    elif estado == "faq":

        if text == "1":
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "ℹ️ Información general\n\n"
                    "Ofrecemos un servicio adaptado a las necesidades de cada cliente.\n"
                    "El proceso es simple:\n"
                    "1️⃣ Nos cuentas qué necesitas\n"
                    "2️⃣ Evaluamos tu caso\n"
                    "3️⃣ Te damos una propuesta personalizada\n\n"
                    "Si deseas una cotización, elige la opción 2️⃣ 😊",
                    number,
                )
            )

        elif text == "2" or "precio" in text or "cotiz" in text:
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "🧾 Cotización personalizada\n\n"
                    "El precio depende de lo que necesites.\n"
                    "Cuéntanos brevemente:\n"
                    "• Qué necesitas\n"
                    "• Para cuándo lo necesitas\n\n"
                    "Un agente te responderá pronto 😊",
                    number,
                )
            )
            notify_agent(number, "Solicitud de cotización")

        elif text == "3":
            active_conversations[number]["estado"] = "menu_principal"
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "Perfecto 👍 Volvemos al menú principal.\n\n"
                    "1️⃣ Conocer el producto\n"
                    "2️⃣ Preguntas frecuentes\n"
                    "3️⃣ Hablar con un agente",
                    number,
                )
            )

        else:
            whatsappservice.SendMessageWhatsapp(
                util.TextMessage(
                    "Selecciona una opción válida:\n\n"
                    "1️⃣ Información general\n"
                    "2️⃣ Cotización personalizada\n"
                    "3️⃣ Volver al menú",
                    number,
                )
            )

    # Enviar respuestas
    for msg in responses:
        whatsappservice.SendMessageWhatsapp(msg)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
