from fastapi import APIRouter, Query, HTTPException

from app.services.sms_gateway_client import SMSGatewayClient
from app.services import contacts as cts
from app.services import history as hist
from app.services import masters as mst

router = APIRouter(prefix="/llm", tags=["llm"])

gateway = SMSGatewayClient()


@router.post("/send")
async def llm_send(phone: str = Query(...), message: str = Query(...)):
    """Envoyer un SMS depuis l'LLM."""
    data = await gateway.send_sms(phone_numbers=[phone], text=message)
    if "error" in data:
        raise HTTPException(status_code=502, detail=data["error"])
    gateway_id = data.get("id") or data.get("data", {}).get("id")
    name = ""
    contact = cts.find_contact_by_phone(phone)
    if contact:
        name = contact["name"]
    hist.record_send(phone, message, to_name=name, gateway_id=gateway_id)
    return {
        "success": True,
        "phone": phone,
        "message": message,
        "gateway_id": gateway_id,
        "contact_name": name or None,
    }


@router.get("/contacts")
async def llm_contacts(search: str | None = Query(None)):
    """Lister ou chercher des contacts depuis l'LLM."""
    contacts = cts.list_contacts(search)
    return {
        "count": len(contacts),
        "contacts": [
            {"id": c["id"], "name": c["name"], "phone": c["phone"], "notes": c["notes"]}
            for c in contacts
        ],
    }


@router.post("/contacts")
async def llm_create_contact(name: str = Query(...), phone: str = Query(...), notes: str = Query("")):
    """Ajouter un contact depuis l'LLM."""
    existing = cts.find_contact_by_phone(phone)
    if existing:
        return {
            "success": True,
            "contact": {"id": existing["id"], "name": existing["name"], "phone": existing["phone"]},
            "note": "Contact déjà existant, aucune création nécessaire",
        }
    contact = cts.create_contact(name, phone, notes)
    return {
        "success": True,
        "contact": {"id": contact["id"], "name": contact["name"], "phone": contact["phone"]},
    }


@router.get("/history")
async def llm_history(limit: int = Query(10, ge=1, le=50)):
    """Derniers envois SMS depuis l'LLM."""
    entries = hist.list_history(limit=limit)
    return {
        "count": len(entries),
        "history": [
            {
                "id": e["id"],
                "to": e["to_name"] or e["to_phone"],
                "phone": e["to_phone"],
                "message": e["message"],
                "status": e["status"],
                "sent_at": e["created_at"],
            }
            for e in entries
        ],
    }


@router.get("/masters")
async def llm_masters():
    """Lister les numéros maîtres depuis l'LLM."""
    masters = mst.list_masters(active_only=True)
    return {
        "count": len(masters),
        "masters": [
            {"id": m["id"], "name": m["name"], "phone": m["phone"]}
            for m in masters
        ],
    }


@router.post("/alert")
async def llm_alert(message: str = Query(...)):
    """Envoyer une alerte urgente à tous les numéros maîtres."""
    masters = mst.list_masters(active_only=True)
    if not masters:
        raise HTTPException(status_code=404, detail="Aucun numéro maître actif configuré")
    phones = [m["phone"] for m in masters]
    data = await gateway.send_sms(
        phone_numbers=phones,
        text=f"[URGENT] {message}",
        priority=100,
    )
    if "error" in data:
        raise HTTPException(status_code=502, detail=data["error"])
    gateway_id = data.get("id") or data.get("data", {}).get("id")
    results = []
    for m in masters:
        hist.record_send(m["phone"], message, to_name=m["name"], gateway_id=gateway_id)
        results.append({"name": m["name"], "phone": m["phone"]})
    return {
        "success": True,
        "message": message,
        "sent_to": len(results),
        "recipients": results,
        "gateway_id": gateway_id,
    }


@router.get("/status")
async def llm_status():
    """État de la passerelle SMS depuis l'LLM."""
    health = await gateway.health()
    return {
        "gateway_reachable": health.get("status") == "ok",
    }
