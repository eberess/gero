from openai.types.chat import ChatCompletionToolParam

TOOLS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "get_inbox",
            "description": "Récupère la liste des derniers emails reçus dans la boîte de réception.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Nombre maximum d'emails à récupérer (par défaut 10)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sent_emails",
            "description": "Récupère la liste des derniers emails envoyés.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Nombre maximum d'emails à récupérer (par défaut 10)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_email",
            "description": "Lit le contenu complet d'un email spécifique par son UID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "uid": {"type": "integer", "description": "L'UID de l'email à lire"},
                    "folder": {"type": "string", "description": "Le dossier, 'INBOX' (reçu) ou 'Sent' (envoyé). Défaut: 'INBOX'"}
                },
                "required": ["uid"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_contact",
            "description": "Cherche un contact dans le carnet d'adresses par son nom.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Le nom du contact à chercher"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "prepare_email",
            "description": "Prépare un email à envoyer. Appelé quand l'utilisateur veut envoyer un message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_name": {"type": "string", "description": "Nom du destinataire"},
                    "to_email": {"type": "string", "description": "Adresse email du destinataire"},
                    "subject": {"type": "string", "description": "Sujet de l'email"},
                    "body": {"type": "string", "description": "Corps de l'email complet et bien rédigé"}
                },
                "required": ["to_email", "subject", "body"]
            }
        }
    },
]
