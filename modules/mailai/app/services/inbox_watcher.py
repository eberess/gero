import asyncio
import re
from openai import OpenAI

from app.dependencies import mail_config
from app.services import db
from app.services import contacts as contacts_svc
from app.services.email_sender import send as send_email
from app.services.imap_client import list_inbox, read_email

AUTO_REPLY_PROMPT = (
    "Tu es G1, un assistant robot de l'équipe GERO. "
    "Tu reçois un email d'un collègue et tu dois y répondre de façon naturelle et amicale en français. "
    "Sois concis, courtois et utile. Tu es nouveau dans l'équipe et content de collaborer avec eux. "
    "Signe toujours par 'G1'."
)


def _extract_email(sender: str) -> str:
    match = re.search(r'<([^>]+)>', sender)
    return match.group(1) if match else sender.strip()


def _sender_name(sender: str) -> str:
    name = sender.split('<')[0].strip().strip('"')
    return name if name else sender


def _is_known_contact(sender: str) -> bool:
    email = _extract_email(sender)
    if contacts_svc.find_by_email(email):
        return True
    name = _sender_name(sender)
    if contacts_svc.find_by_name(name):
        return True
    return False


def _is_processed(uid: int) -> bool:
    conn = db.get_connection()
    row = conn.execute("SELECT 1 FROM processed_uids WHERE uid = ?", (uid,)).fetchone()
    return row is not None


def _mark_processed(uid: int, sender: str) -> None:
    conn = db.get_connection()
    conn.execute("INSERT OR IGNORE INTO processed_uids (uid, sender) VALUES (?, ?)", (uid, sender))
    conn.commit()


def _generate_reply(email_text: str, sender: str) -> str:
    client = OpenAI(api_key=mail_config.openai_api_key)
    response = client.chat.completions.create(
        model=mail_config.openai_model,
        messages=[
            {"role": "system", "content": AUTO_REPLY_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Voici l'email que j'ai reçu de {sender} :\n\n"
                    f"{email_text[:2000]}\n\n"
                    f"Génère une réponse appropriée."
                ),
            },
        ],
        temperature=0.5,
    )
    return response.choices[0].message.content or "Merci pour ton message, j'y reviens rapidement !"


def check_and_reply() -> int:
    replied = 0
    try:
        emails = list_inbox(limit=30)
    except Exception as e:
        print(f"[inbox_watcher] Erreur IMAP: {e}")
        return 0

    for email in reversed(emails):
        if _is_processed(email.uid):
            continue
        if not _is_known_contact(email.sender):
            continue

        print(f"[inbox_watcher] Nouveau mail de {email.sender} (UID {email.uid})")
        try:
            full = read_email(email.uid)
            if not full:
                continue
            body = full.body_text or "(pas de contenu texte)"
            reply_text = _generate_reply(body, email.sender)

            reply_to = _extract_email(email.sender)
            reply_subject = f"RE: {email.subject}" if email.subject else "RE:"
            send_email(to_email=reply_to, subject=reply_subject, body=reply_text)
            _mark_processed(email.uid, email.sender)
            replied += 1
            print(f"[inbox_watcher] Réponse envoyée à {email.sender}")
        except Exception as e:
            print(f"[inbox_watcher] Erreur pour UID {email.uid}: {e}")

    return replied


async def watch_loop(interval: int = 60):
    print(f"[inbox_watcher] Démarrage (intervalle={interval}s)")
    while True:
        try:
            count = await asyncio.to_thread(check_and_reply)
            if count:
                print(f"[inbox_watcher] {count} réponse(s) envoyée(s)")
        except Exception as e:
            print(f"[inbox_watcher] Erreur boucle: {e}")
        await asyncio.sleep(interval)
