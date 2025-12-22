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


def TextFormatMessage(number):
    return {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "text",
        "text": {
            "body": "*text-message-content* - _hola usuario_ - ~hola~ - ``` hola ```"
        },
    }


def ImageMessage(number):
    return {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "image",
        "image": {
            "link": "https://biostoragecloud.blob.core.windows.net/resource-udemy-whatsapp-node/image_whatsapp.png"
        },
    }


def AudioMessage(number):
    return {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "audio",
        "audio": {
            "link": "https://biostoragecloud.blob.core.windows.net/resource-udemy-whatsapp-node/audio_whatsapp.mp3"
        },
    }


def VideoMessage(number):
    return {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "video",
        "video": {
            "link": "https://biostoragecloud.blob.core.windows.net/resource-udemy-whatsapp-node/video_whatsapp.mp4"
        },
    }


def DocumentMessage(number):
    return {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "document",
        "document": {
            "link": "https://biostoragecloud.blob.core.windows.net/resource-udemy-whatsapp-node/document_whatsapp.pdf"
        },
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


def ButtonsMessage(number):
    return {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "¿Confirmas tu registro?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "001", "title": "Sí"}},
                    {"type": "reply", "reply": {"id": "002", "title": "No"}},
                ]
            },
        },
    }


def ListMessage(number):
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
                "sections": [
                    {
                        "title": "Compra y venta",
                        "rows": [
                            {
                                "id": "buy",
                                "title": "Comprar",
                                "description": "Compra el mejor producto",
                            },
                            {
                                "id": "sell",
                                "title": "Vender",
                                "description": "Vende tus productos",
                            },
                        ],
                    },
                    {
                        "title": "📍 Atención",
                        "rows": [
                            {
                                "id": "agency",
                                "title": "Agencia",
                                "description": "Visita nuestra agencia",
                            },
                            {
                                "id": "contact",
                                "title": "Contacto",
                                "description": "Un agente te asistirá",
                            },
                        ],
                    },
                ],
            },
        },
    }
