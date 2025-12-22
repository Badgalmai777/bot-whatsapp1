from flask import Flask, request
import os
import util
import whatsappservice
import time
import threading

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
def VerifyToken():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token and challenge and token == ACCESS_TOKEN:
        return challenge
    return "", 400


# Recepción de mensajes
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

        # Actualiza la conversación activa
        update_conversation(number)
        ProcessMessage(text, number)

        print(f"Mensaje recibido: {text} de {number}")
        return "EVENT_RECEIVED", 200
    except Exception as e:
        print(e)
        return "EVENT_RECEIVED", 200


# Procesa mensajes según el guion
def ProcessMessage(text, number):
    text = text.lower()
    responses = []

    # SALUDO y MENÚ para cualquier mensaje recibido
    whatsappservice.SendMessageWhatsapp(util.TextMessage(
    "¡Hola! 👋 Soy [Nombre del Bot], tu asistente inteligente.\n\n"
    "Por favor, elige una opción:\n"
    "1️⃣ Conocer el producto\n"
    "2️⃣ Consejos o dudas frecuentes\n"
    "3️⃣ Hablar con un agente",
    number
    ))

    # Terminar aquí para que no se ejecuten otras respuestas en este primer mensaje
    return

    # ---- A partir de aquí van las respuestas según opciones ----
    # Opción 1: Conocer el producto
    if text.startswith("1") or "conocer el producto" in text:
        responses.append(
            util.TextMessage(
                "[Nombre del Bot] automatiza tus mensajes, organiza pedidos y te muestra estadísticas en tiempo real. Todo en un solo lugar. 😎",
                number,
            )
        )

    # Opción 2: Consejos o dudas frecuentes
    elif text.startswith("2") or "consejos" in text or "dudas" in text:
        responses.append(
            util.TextMessage(
                "Puedes preguntarme sobre:\n"
                "a) Cómo funciona el bot\n"
                "b) Precios\n"
                "c) Integraciones con tu negocio",
                number,
            )
        )

    # Sub-opciones de la opción 2
    elif "a" in text or "cómo funciona" in text:
        responses.append(
            util.TextMessage(
                "[Nombre del Bot] responde mensajes al instante, organiza pedidos o citas, y te muestra estadísticas en tiempo real. 😎",
                number,
            )
        )
    elif "b" in text or "precios" in text:
        responses.append(
            util.TextMessage(
                "Planes disponibles:\n"
                "• Básico: respuestas automáticas y organización de mensajes\n"
                "• Avanzado: todo lo del básico + reportes y estadísticas\n"
                "• Premium: todo + integraciones y soporte prioritario",
                number,
            )
        )
    elif "c" in text or "integraciones" in text:
        responses.append(
            util.TextMessage(
                "Se integra con WhatsApp, Facebook, Instagram, tu web y CRMs populares. Centraliza todo en un solo lugar.",
                number,
            )
        )

    # Opción 3: Hablar con un agente
    elif text.startswith("3") or "agente" in text or "hablar con un agente" in text:
        responses.append(
            util.TextMessage(
                "Conectándote con un agente humano… ¡un momento por favor! 🕒", number
            )
        )
        notify_agent(number, "Solicitud de agente")

    # Mensaje por defecto
    else:
        responses.append(
            util.TextMessage(
                "Lo siento, no entendí tu mensaje. Por favor selecciona una opción del menú.",
                number,
            )
        )

    # Enviar todas las respuestas
    for msg in responses:
        whatsappservice.SendMessageWhatsapp(msg)


# Ejecuta la app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

