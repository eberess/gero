from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

from mailai import ai, contacts, email_sender, history
from mailai.config import config
from mailai.imap_client import list_inbox, list_sent, read_email


class EngineResult:
    def __init__(
        self,
        success: bool,
        message: str,
        to_name: str = "",
        to_email: str = "",
        subject: str = "",
        body: str = "",
    ) -> None:
        self.success = success
        self.message = message
        self.to_name = to_name
        self.to_email = to_email
        self.subject = subject
        self.body = body


class ChatResult:
    def __init__(self, text: str = "", pending_email: Optional[EngineResult] = None):
        self.text = text
        self.pending_email = pending_email


def process_chat(messages: List[Dict[str, Any]]) -> ChatResult:
    valid, errors = config.is_valid
    if not valid:
        return ChatResult(text=f"Configuration invalide : {', '.join(errors)}")

    while True:
        msg = ai.chat(messages)
        
        # Append AI message to history
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            # Simple text response
            return ChatResult(text=msg.content or "")

        # Handle tool calls
        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            args_str = tool_call.function.arguments
            
            try:
                args = json.loads(args_str)
            except json.JSONDecodeError:
                args = {}

            tool_result_str = ""

            if fn_name == "prepare_email":
                to_name = args.get("to_name", "")
                to_email = args.get("to_email", "")
                subject = args.get("subject", "")
                body = args.get("body", "")

                if not to_email and to_name:
                    contact = contacts.find_by_name(to_name)
                    if contact:
                        to_email = contact.email

                if not to_email:
                    return ChatResult(
                        text=f"Adresse email introuvable pour « {to_name} ». Utilise /add {to_name} <email> pour l'ajouter.",
                        pending_email=EngineResult(False, "Email manquant", to_name, "", subject, body)
                    )

                pending = EngineResult(
                    True,
                    "Prêt à envoyer. Confirme avec `/send` ou `/confirm`.",
                    to_name,
                    to_email,
                    subject,
                    body
                )
                
                # We stop the loop and return the pending email to the user
                # Provide a fake successful execution to the model history in case it continues later
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": "L'email a été préparé et est en attente de confirmation par l'utilisateur."
                })
                return ChatResult(text=msg.content or "Email préparé ! Vérifie les détails ci-dessous.", pending_email=pending)

            elif fn_name == "get_inbox":
                limit = args.get("limit", 10)
                try:
                    emails = list_inbox(limit=limit)
                    res = [{"uid": e.uid, "date": e.date, "sender": e.sender, "subject": e.subject} for e in emails]
                    tool_result_str = json.dumps(res, ensure_ascii=False)
                except Exception as e:
                    tool_result_str = f"Erreur: {str(e)}"
                    
            elif fn_name == "get_sent_emails":
                limit = args.get("limit", 10)
                try:
                    emails = list_sent(limit=limit)
                    res = [{"uid": e.uid, "date": e.date, "recipient": e.recipient, "subject": e.subject} for e in emails]
                    tool_result_str = json.dumps(res, ensure_ascii=False)
                except Exception as e:
                    tool_result_str = f"Erreur: {str(e)}"
                    
            elif fn_name == "read_email":
                uid = args.get("uid")
                folder = args.get("folder", "INBOX")
                if uid:
                    try:
                        e = read_email(uid, folder=folder)
                        if e:
                            tool_result_str = json.dumps({
                                "uid": e.uid, "date": e.date, "sender": e.sender, 
                                "recipient": e.recipient, "subject": e.subject,
                                "body_text": e.body_text
                            }, ensure_ascii=False)
                        else:
                            tool_result_str = "Email introuvable."
                    except Exception as ex:
                        tool_result_str = f"Erreur: {str(ex)}"
                else:
                    tool_result_str = "Erreur: UID manquant."
                    
            elif fn_name == "find_contact":
                name = args.get("name", "")
                found = contacts.find_by_name(name)
                if found:
                    tool_result_str = json.dumps({"name": found.name, "email": found.email}, ensure_ascii=False)
                else:
                    tool_result_str = "Contact introuvable."
            else:
                tool_result_str = "Fonction inconnue."

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result_str
            })

        # Loop continues to let AI respond after tool executions


def confirm_and_send(to_name: str, to_email: str, subject: str, body: str) -> EngineResult:
    try:
        email_sender.send(to_email=to_email, subject=subject, body=body, to_name=to_name)
        history.record_sent(to_name, to_email, subject, body)
        return EngineResult(True, "Email envoyé avec succès !", to_name, to_email, subject, body)
    except Exception as e:
        error_msg = str(e)
        history.record_failed(to_name, to_email, subject, body, error_msg)
        return EngineResult(False, f"Échec de l'envoi : {error_msg}", to_name, to_email, subject, body)

