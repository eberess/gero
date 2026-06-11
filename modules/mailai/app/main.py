import asyncio
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.dependencies import mail_config
from app.llm import router as llm_router
from app.models import EmailToSend, ContactCreate
from app.services import contacts as contacts_svc
from app.services import history as history_svc
from app.services.imap_client import list_inbox, list_sent, read_email
from app.services.email_sender import send as send_email
from app.services.db import close as db_close
from app.services.inbox_watcher import watch_loop

app = FastAPI(
    title="geroMailAI API",
    description="Assistant email intelligent — OVH SMTP/IMAP + OpenAI",
    version="1.0.0",
)

GENERIC_ERRORS = {
    400: "Requête invalide",
    401: "Non authentifié",
    403: "Accès refusé",
    404: "Ressource non trouvée",
    422: "Données invalides",
    500: "Erreur interne du serveur",
}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": GENERIC_ERRORS.get(exc.status_code, "Erreur")},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": GENERIC_ERRORS[500]})


app.include_router(llm_router)


_watcher_task = None


@app.on_event("startup")
async def startup():
    global _watcher_task
    _watcher_task = asyncio.create_task(watch_loop(interval=60))
    print("[main] Inbox watcher démarré")


@app.on_event("shutdown")
def shutdown():
    global _watcher_task
    if _watcher_task:
        _watcher_task.cancel()
    db_close()


@app.get("/")
def read_root():
    return {"status": "ok", "service": "geroMailAI"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/mail/inbox")
async def get_inbox(limit: int = Query(10, ge=1, le=50)):
    try:
        emails = list_inbox(limit=limit)
        return {"data": {"count": len(emails), "emails": [e.to_dict() for e in emails]}}
    except Exception as e:
        return {"data": {"error": f"Erreur IMAP: {str(e)}"}}


@app.get("/mail/sent")
async def get_sent(limit: int = Query(10, ge=1, le=50)):
    try:
        emails = list_sent(limit=limit)
        return {"data": {"count": len(emails), "emails": [e.to_dict() for e in emails]}}
    except Exception as e:
        return {"data": {"error": f"Erreur IMAP: {str(e)}"}}


@app.get("/mail/{uid}")
async def get_email(uid: int, folder: str = Query("INBOX")):
    try:
        email_msg = read_email(uid, folder=folder)
        if not email_msg:
            return {"data": {"error": "Email non trouvé"}}
        return {"data": email_msg.to_dict()}
    except Exception as e:
        return {"data": {"error": f"Erreur IMAP: {str(e)}"}}


@app.post("/mail/send")
async def send_email_endpoint(body: EmailToSend):
    try:
        send_email(to_email=body.to_email, subject=body.subject,
                   body=body.body, to_name=body.to_name)
        history_svc.record_sent(body.to_name, body.to_email, body.subject, body.body)
        return {"data": {"success": True, "message": f"Email envoyé à {body.to_name or body.to_email}"}}
    except Exception as e:
        history_svc.record_failed(body.to_name, body.to_email, body.subject, body.body, str(e))
        return {"data": {"error": f"Échec envoi: {str(e)}"}}


@app.get("/contacts")
async def list_contacts(query: str = Query("")):
    if query:
        results = contacts_svc.search(query)
    else:
        results = contacts_svc.list_all()
    return {"data": {"count": len(results), "contacts": [c.to_dict() for c in results]}}


@app.post("/contacts")
async def add_contact(body: ContactCreate):
    existing = contacts_svc.find_by_name(body.name)
    if existing:
        return {"data": {"error": f"Le contact '{body.name}' existe déjà", "contact": existing.to_dict()}}
    contact = contacts_svc.add(body.name, body.email, body.notes)
    return {"data": {"contact": contact.to_dict()}}


@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int):
    if contacts_svc.delete(contact_id):
        return {"data": {"success": True}}
    return {"data": {"error": "Contact non trouvé"}}


@app.get("/history")
async def get_history(limit: int = Query(20, ge=1, le=100)):
    entries = history_svc.list_recent(limit=limit)
    return {"data": {"count": len(entries), "entries": [e.to_dict() for e in entries]}}
