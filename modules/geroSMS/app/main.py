from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.dependencies import sms_config
from app.services.sms_gateway_client import SMSGatewayClient
from app.services import contacts as cts
from app.services import history as hist
from app.models import ContactCreate, ContactUpdate, SendSMSRequest, SendSMSBatchRequest
from app.llm import router as llm_router

app = FastAPI(
    title="geroSMS API",
    description="SMS microservice for GERO — android-sms-gateway",
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

gateway = SMSGatewayClient()


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


@app.get("/")
def read_root():
    return {"status": "ok", "service": "geroSMS"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/sms/gateway/health")
async def gateway_health():
    data = await gateway.health()
    return {"data": data}


@app.get("/sms/devices")
async def list_devices():
    data = await gateway.get_devices()
    if "error" in data:
        raise HTTPException(status_code=502, detail=data["error"])
    return {"data": data.get("data", data)}


@app.get("/sms/messages")
async def list_messages(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    device_id: str | None = None,
):
    data = await gateway.get_messages(page, per_page, status, device_id)
    if "error" in data:
        raise HTTPException(status_code=502, detail=data["error"])
    return {"data": data.get("data", data)}


@app.post("/sms/send")
async def send_sms(req: SendSMSRequest):
    data = await gateway.send_sms(
        phone_numbers=[req.phone],
        text=req.message,
        device_id=req.device_id,
        sim_number=req.sim_number,
        priority=req.priority,
    )
    if "error" in data:
        hist.record_failure(req.phone, req.message, data["error"])
        raise HTTPException(status_code=502, detail=data["error"])
    gateway_id = data.get("id") or data.get("data", {}).get("id")
    hist.record_send(req.phone, req.message, gateway_id=gateway_id)
    return {"data": data}


@app.post("/sms/send/batch")
async def send_sms_batch(req: SendSMSBatchRequest):
    data = await gateway.send_sms(
        phone_numbers=req.phone_numbers,
        text=req.message,
        device_id=req.device_id,
        sim_number=req.sim_number,
        priority=req.priority,
    )
    if "error" in data:
        for phone in req.phone_numbers:
            hist.record_failure(phone, req.message, data["error"])
        raise HTTPException(status_code=502, detail=data["error"])
    gateway_id = data.get("id") or data.get("data", {}).get("id")
    for phone in req.phone_numbers:
        hist.record_send(phone, req.message, gateway_id=gateway_id)
    return {"data": data}


@app.get("/contacts")
async def list_contacts(search: str | None = None):
    return {"data": cts.list_contacts(search)}


@app.get("/contacts/{contact_id}")
async def get_contact(contact_id: int):
    contact = cts.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact introuvable")
    return {"data": contact}


@app.post("/contacts")
async def create_contact(req: ContactCreate):
    existing = cts.find_contact_by_phone(req.phone)
    if existing:
        raise HTTPException(status_code=409, detail="Ce numéro existe déjà")
    contact = cts.create_contact(req.name, req.phone, req.notes)
    return {"data": contact}


@app.put("/contacts/{contact_id}")
async def update_contact(contact_id: int, req: ContactUpdate):
    contact = cts.update_contact(contact_id, req.name, req.phone, req.notes)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact introuvable")
    return {"data": contact}


@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int):
    if not cts.delete_contact(contact_id):
        raise HTTPException(status_code=404, detail="Contact introuvable")
    return {"data": {"deleted": True}}


@app.get("/history")
async def list_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: str | None = None,
):
    return {"data": hist.list_history(limit, offset, status)}


@app.get("/history/{entry_id}")
async def get_history_entry(entry_id: int):
    entry = hist.get_history_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entrée introuvable")
    return {"data": entry}
