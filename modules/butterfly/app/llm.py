from fastapi import APIRouter, Query, HTTPException
from app.dependencies import supabase_client
from datetime import date, timedelta

router = APIRouter(prefix="/llm", tags=["llm"])

_CERTIF_FIELDS = [
    ("fpi", "FPI"),
    ("fphi", "FPHI"),
    ("certif", "Certification sûreté"),
    ("carte_pro", "Carte professionnelle"),
    ("badge_date_expiration", "Badge d'accès"),
]


def _fmt_date(d: str | None) -> str | None:
    if not d:
        return None
    return d[:10]


def _statut(d: str | None, today: date) -> str:
    if not d:
        return "non renseigné"
    d_date = date.fromisoformat(d[:10])
    if d_date < today:
        return "expiré"
    if d_date <= today + timedelta(days=90):
        return "expire bientôt"
    return "valide"


@router.get("/agent")
async def llm_agent(nom: str = Query(...), prenom: str = Query("")):
    data = await supabase_client.get_agent_full_profile(nom, prenom)
    if "error" in data:
        raise HTTPException(status_code=502, detail="Erreur de la base formations")

    formations = data.get("formations", [])
    if not formations:
        return {
            "agent": f"{prenom} {nom}".strip(),
            "trouve": False,
            "message": "Aucun agent trouvé",
        }

    today = date.today()
    f = formations[0]
    certifs = [
        {"certification": label, "date": _fmt_date(f.get(field)), "statut": _statut(f.get(field), today)}
        for field, label in _CERTIF_FIELDS
        if f.get(field)
    ]

    expirees = [c for c in certifs if c["statut"] == "expiré"]
    imminentes = [c for c in certifs if c["statut"] == "expire bientôt"]

    if expirees:
        message = f"Attention, {len(expirees)} certification(s) expirée(s)"
    elif imminentes:
        message = f"{len(imminentes)} certification(s) expire(nt) bientôt"
    else:
        message = "Tout est à jour"

    return {
        "agent": f"{f.get('prenom', '')} {f.get('nom', '')}".strip(),
        "typo": f.get("typo"),
        "trouve": True,
        "message": message,
        "certifications": certifs,
        "badges": data.get("badges", []),
    }


@router.get("/alerts")
async def llm_alerts():
    today = date.today()

    expired = await supabase_client.get_expired(today.isoformat())
    if "error" in expired:
        raise HTTPException(status_code=502, detail="Erreur de la base formations")

    expiring = await supabase_client.get_expiring_soon(30)
    if "error" in expiring:
        raise HTTPException(status_code=502, detail="Erreur de la base formations")

    seen = set()
    alerts = []

    for f in expired.get("formations", []):
        key = f"{f.get('prenom', '')} {f.get('nom', '')}".strip()
        seen.add(key)
        expired_fields = [
            label for field, label in _CERTIF_FIELDS
            if f.get(field) and date.fromisoformat(f[field][:10]) < today
        ]
        if expired_fields:
            alerts.append({"agent": key, "typo": f.get("typo"), "alerte": "expiré", "documents": expired_fields})

    for f in expiring.get("formations", []):
        key = f"{f.get('prenom', '')} {f.get('nom', '')}".strip()
        if key in seen:
            continue
        seen.add(key)
        soon_fields = [
            label for field, label in _CERTIF_FIELDS
            if f.get(field)
            and today <= date.fromisoformat(f[field][:10]) <= today + timedelta(days=30)
        ]
        if soon_fields:
            alerts.append({"agent": key, "typo": f.get("typo"), "alerte": "expire bientôt", "documents": soon_fields})

    return {
        "date": today.isoformat(),
        "total_alerts": len(alerts),
        "expired_count": len(expired.get("formations", [])),
        "expiring_count": len(expiring.get("formations", [])),
        "alerts": alerts[:50],
    }


@router.get("/check-badge")
async def llm_check_badge(numero: str = Query(...)):
    data = await supabase_client.search_badge(numero=numero)
    if "error" in data:
        raise HTTPException(status_code=502, detail="Erreur de la base badges")

    badges = data.get("badges", [])
    if not badges:
        return {"trouve": False, "message": f"Aucun badge trouvé pour {numero}"}

    b = badges[0]
    today = date.today()
    date_fin = b.get("dateFinAccordee")

    if date_fin and date.fromisoformat(date_fin) < today:
        validite = "expiré"
    elif date_fin:
        validite = "valide"
    else:
        validite = "non déterminée"

    return {
        "trouve": True,
        "badge": {
            "numero": b.get("numeroBadge"),
            "nom": f"{b.get('prenom', '')} {b.get('nom', '')}".strip(),
            "etat": b.get("etat"),
            "date_fin": date_fin,
            "validite": validite,
            "entreprise": b.get("entreprise"),
            "email": b.get("email"),
        },
    }


@router.get("/stats")
async def llm_stats():
    data = await supabase_client.get_compliance_stats()
    if "error" in data:
        raise HTTPException(status_code=502, detail="Erreur de la base formations")

    total = data.get("total_agents", 0)
    expired = data.get("expired", 0)
    valid = data.get("valid", 0)
    pct = round(valid / total * 100, 1) if total else 0

    typo_data = await supabase_client.get_typo_stats()
    typo_stats = typo_data.get("typo_stats", []) if "error" not in typo_data else []

    return {
        "total_agents": total,
        "taux_conformite_pct": pct,
        "a_jour": valid,
        "expires": expired,
        "repartition_typo": typo_stats,
    }
