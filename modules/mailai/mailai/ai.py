from __future__ import annotations

import json
from typing import Any, List, Dict

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

from mailai.config import config


SYSTEM_PROMPT = """Tu es MailAI, un assistant email intelligent.
Ton rôle est d'aider l'utilisateur à gérer sa boîte mail (lire, chercher des contacts, préparer des emails).
Tu disposes d'outils (fonctions) pour interagir avec le système.
Utilise ces outils lorsque c'est nécessaire. Si l'utilisateur te demande de lire ses mails, utilise get_inbox ou get_sent_emails. S'il te demande le détail d'un mail, utilise read_email.
Pour envoyer un mail, utilise toujours l'outil prepare_email. Si l'utilisateur ne donne pas l'adresse email, cherche le contact avec find_contact d'abord, ou demande à l'utilisateur.
Ne demande jamais à l'utilisateur de fournir manuellement un UID, cherche les emails avec tes outils.
Si tu n'as pas de réponse pertinente via les outils, réponds naturellement en français.
Sois concis, courtois et utile."""

TOOLS: List[ChatCompletionToolParam] = [
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
                    "folder": {"type": "string", "description": "Le dossier de l'email, e.g. 'INBOX' (reçu) ou 'sent' (envoyé). Défaut: 'INBOX'"}
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
            "description": "Prépare un email à envoyer. Doit être appelé lorsque l'utilisateur veut envoyer un message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_name": {"type": "string", "description": "Nom du destinataire"},
                    "to_email": {"type": "string", "description": "Adresse email du destinataire (utiliser find_contact si inconnu)"},
                    "subject": {"type": "string", "description": "Sujet de l'email"},
                    "body": {"type": "string", "description": "Corps de l'email bien rédigé et complet"}
                },
                "required": ["to_email", "subject", "body"]
            }
        }
    }
]


def chat(messages: List[Dict[str, Any]]) -> Any:
    """
    Appelle l'API OpenAI avec l'historique des messages et les outils disponibles.
    Renvoie le message de réponse (qui peut inclure des tool_calls).
    """
    client = OpenAI(api_key=config.openai_api_key)
    
    # Ensure system prompt is present
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        
    response = client.chat.completions.create(
        model=config.openai_model,
        messages=messages, # type: ignore
        tools=TOOLS,
        temperature=0.3,
    )
    
    return response.choices[0].message
