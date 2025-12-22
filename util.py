def GetTextUser(message):
    text = ""
    typeMessage = message["type"]

    if typeMessage == "text":
        text = message["text"]["body"]

    elif typeMessage == "interactive":
        interactive = message["interactive"]
        typeInteractive = interactive["type"]

        if typeInteractive == "button_reply":
            text = interactive["button_reply"]["title"]

        elif typeInteractive == "list_reply":
            text = interactive["list_reply"]["title"]

    return text


def TextMessage(text, number):
    return {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "text",
        "text": {"body": text},
    }


def LocationMessage(number):
    return {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "location",
        "location": {
            "latitude": "-12.067158831865067",
            "longitude": "-77.03377940839486",
            "name": "Estadio Nacional del Perú",
            "address": "C. José Díaz s/n, Cercado de Lima 15046",
        },
    }


# Botones de confirmación simple (opcional)
def ButtonsMessage(number, text="¿Confirmas tu registro?", buttons=None):
    if buttons is None:
        buttons = [
            {"type": "reply", "reply": {"id": "001", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "002", "title": "No"}},
        ]

    return {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {"buttons": buttons},
        },
    }


# Menú principal del bot
def ListMessage(number, options=None):
    if options is None:
        options = [
            "1️⃣ Conocer el producto",
            "2️⃣ Consejos o dudas frecuentes",
            "3️⃣ Hablar con un agente",
        ]

    # Convertimos las opciones en rows para WhatsApp
    rows = [
        {"id": str(i + 1), "title": opt, "description": ""}
        for i, opt in enumerate(options)
    ]

    return {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "✅ Tengo estas opciones"},
            "footer": {"text": "Selecciona una opción"},
            "action": {
                "button": "Ver opciones",
                "sections": [{"title": "Menú principal", "rows": rows}],
            },
        },
    }

