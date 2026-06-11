import json
from fastapi import APIRouter, HTTPException
from openai import OpenAI

from app.dependencies import mail_config
from app.tools import TOOLS
from app.services import contacts as contacts_svc
from app.services import history as history_svc
from app.services.imap_client import list_inbox, list_sent, read_email
from app.services.email_sender import send as send_email
from app.services.supabase_client import supabase

router = APIRouter(prefix="/llm", tags=["llm"])

SYSTEM_PROMPT = """Tu es MailAI, un assistant email intelligent.
Ton rôle est d'aider l'utilisateur à gérer sa boîte mail (lire, chercher des contacts, préparer des emails).
Tu disposes d'outils (fonctions) pour interagir avec le système.
Utilise ces outils lorsque c'est nécessaire.
Si l'utilisateur te demande de lire ses mails, utilise get_inbox ou get_sent_emails.
Pour envoyer un mail, utilise toujours l'outil prepare_email.
Si l'utilisateur ne donne pas l'adresse email, cherche le contact avec find_contact d'abord, ou demande à l'utilisateur.
Ne demande jamais à l'utilisateur de fournir manuellement un UID, cherche les emails avec tes outils.
Réponds naturellement en français. Sois concis, courtois et utile."""


async def _execute_tool(fn_name: str, args: dict) -> str:
    if fn_name == "get_inbox":
        limit = args.get("limit", 10)
        try:
            emails = list_inbox(limit=limit)
            res = [{"uid": e.uid, "date": e.date, "sender": e.sender, "subject": e.subject} for e in emails]
            return json.dumps(res, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    elif fn_name == "get_sent_emails":
        limit = args.get("limit", 10)
        try:
            emails = list_sent(limit=limit)
            res = [{"uid": e.uid, "date": e.date, "recipient": e.recipient, "subject": e.subject} for e in emails]
            return json.dumps(res, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    elif fn_name == "read_email":
        uid = args.get("uid")
        folder = args.get("folder", "INBOX")
        if uid:
            try:
                e = read_email(uid, folder=folder)
                if e:
                    return json.dumps(e.to_dict(), ensure_ascii=False)
                return json.dumps({"error": "Email introuvable"}, ensure_ascii=False)
            except Exception as ex:
                return json.dumps({"error": str(ex)}, ensure_ascii=False)
        return json.dumps({"error": "UID manquant"}, ensure_ascii=False)

    elif fn_name == "find_contact":
        name = args.get("name", "")
        found = contacts_svc.find_by_name(name)
        if found:
            return json.dumps({"name": found.name, "email": found.email}, ensure_ascii=False)
        agents = await supabase.search_contact(name)
        if agents:
            a = agents[0]
            return json.dumps({"name": f"{a.get('prenom','')} {a.get('nom','')}".strip(), "email": a.get("mail")}, ensure_ascii=False)
        return json.dumps({"error": "Contact introuvable"}, ensure_ascii=False)

    elif fn_name == "prepare_email":
        to_name = args.get("to_name", "")
        to_email = args.get("to_email", "")
        subject = args.get("subject", "")
        body = args.get("body", "")

        if not to_email and to_name:
            contact = contacts_svc.find_by_name(to_name)
            if contact:
                to_email = contact.email
            if not to_email:
                agents = await supabase.search_contact(to_name)
                if agents:
                    to_email = agents[0].get("mail", "")

        if not to_email:
            return json.dumps({"error": f"Adresse email introuvable pour '{to_name}'"}, ensure_ascii=False)

        try:
            send_email(to_email=to_email, subject=subject, body=body, to_name=to_name)
            history_svc.record_sent(to_name, to_email, subject, body)
            return json.dumps({"success": True, "message": f"Email envoyé à {to_name or to_email}"}, ensure_ascii=False)
        except Exception as e:
            history_svc.record_failed(to_name, to_email, subject, body, str(e))
            return json.dumps({"error": f"Échec de l'envoi: {str(e)}"}, ensure_ascii=False)

    return json.dumps({"error": f"Fonction inconnue: {fn_name}"}, ensure_ascii=False)


async def process_chat(messages: list[dict]) -> dict:
    client = OpenAI(api_key=mail_config.openai_api_key)
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    max_turns = 10
    turn = 0

    while turn < max_turns:
        turn += 1
        response = client.chat.completions.create(
            model=mail_config.openai_model,
            messages=messages,
            tools=TOOLS,
            temperature=0.3,
        )
        msg = response.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return {"response": msg.content or "", "messages": messages}

        for tool_call in msg.tool_calls:
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}
            tool_result = await _execute_tool(tool_call.function.name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            })

    return {"response": "Désolé, je n'ai pas pu terminer le traitement.", "messages": messages}


@router.post("/chat")
async def llm_chat(body: dict):
    message = body.get("message", "")
    history = body.get("messages", [])

    if not message and not history:
        raise HTTPException(status_code=400, detail="Message requis")

    msgs = list(history)
    if message:
        msgs.append({"role": "user", "content": message})

    result = await process_chat(msgs)
    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    return result


@router.post("/send")
async def llm_send(body: dict):
    to_email = body.get("to_email", "")
    to_name = body.get("to_name", "")
    subject = body.get("subject", "")
    message_body = body.get("body", "")

    if not to_email:
        raise HTTPException(status_code=400, detail="to_email requis")
    if not message_body:
        raise HTTPException(status_code=400, detail="body requis")

    try:
        send_email(to_email=to_email, subject=subject, body=message_body, to_name=to_name)
        history_svc.record_sent(to_name, to_email, subject, message_body)
        return {"success": True, "message": f"Email envoyé à {to_name or to_email}"}
    except Exception as e:
        history_svc.record_failed(to_name, to_email, subject, message_body, str(e))
        raise HTTPException(status_code=502, detail=f"Échec envoi: {str(e)}")


@router.get("/inbox")
async def llm_inbox(limit: int = 10):
    try:
        emails = list_inbox(limit=limit)
        return {"count": len(emails), "emails": [e.to_dict() for e in emails]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur IMAP: {str(e)}")


@router.get("/sent")
async def llm_sent(limit: int = 10):
    try:
        emails = list_sent(limit=limit)
        return {"count": len(emails), "emails": [e.to_dict() for e in emails]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur IMAP: {str(e)}")


@router.get("/contacts")
async def llm_contacts(query: str = ""):
    if query:
        results = contacts_svc.search(query)
    else:
        results = contacts_svc.list_all()
    return {"count": len(results), "contacts": [c.to_dict() for c in results]}
