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

# Diccionario para conversaciones activas {number: last_message_timestamp}
active_conversations = {}


# Función para actualizar timestamp de la conversación
def update_conversation(number):
    active_conversations[number] = time.time()


# Función para revisar conversaciones inactivas y notificar al agente
def check_inactive_conversations():
    while True:
        now = time.time()
        inactive = []
        for number, last_time in active_conversations.items():
            if now - last_time > INACTIVITY_TIMEOUT:
                inactive.append(number)
        for number in inactive:
            print(f"Conversación con {number} terminada por inactividad")
            notify_agent(number, "Cliente no respondió después de 10 minutos")
            del active_conversations[number]
        time.sleep(60)  # Revisa cada minuto


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


# Procesa mensajes según el guion (solo opciones 1,2,3)
def process_message(text, number):
    text = text.lower().strip()  # Normalizamos el texto

    opciones_validas = ["1", "2", "3"]

    # ---- SALUDO INICIAL por usuario ----
    if number not in active_conversations or not hasattr(active_conversations[number], "saludo_enviado"):
        whatsappservice.SendMessageWhatsapp(
            util.TextMessage(
                "¡Hola! 👋 Soy whatsappbot, tu asistente inteligente.\n\n"
                "Por favor, elige una opción:\n"
                "1️⃣ Conocer el producto\n"
                "2️⃣ Consejos o dudas frecuentes\n"
                "3️⃣ Hablar con un agente",
                number
            )
        )
        active_conversations[number] = {"last_time": time.time(), "saludo_enviado": True}
        return

    responses = []

    # ---- RESPONDER SEGÚN OPCIÓN ----
    if text == "1":
        responses.append(
            util.TextMessage(
                "[Nombre del Bot] automatiza tus mensajes, organiza pedidos y te muestra estadísticas en tiempo real. Todo en un solo lugar. 😎",
                number,
            )
        )
    elif text == "2":
        responses.append(
            util.TextMessage(
                "Puedes preguntarme cualquier cosa relacionada con nuestros productos o servicios. 😊",
                number,
            )
        )
    elif text == "3":
        responses.append(
            util.TextMessage(
                "Conectándote con un agente humano… ¡un momento por favor! 🕒",
                number,
            )
        )
        notify_agent(number, "Solicitud de agente")
    else:
        responses.append(
            util.TextMessage(
                "Lo siento, no hay esa opción. Por favor selecciona una opción del menú:\n"
                "1️⃣ Conocer el producto\n"
                "2️⃣ Consejos o dudas frecuentes\n"
                "3️⃣ Hablar con un agente",
                number,
            )
        )

    # Enviar todas las respuestas
    for msg in responses:
        whatsappservice.SendMessageWhatsapp(msg)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
