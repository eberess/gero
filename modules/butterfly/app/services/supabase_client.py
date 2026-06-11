import httpx
import os
from datetime import date, timedelta
from typing import Any

_FORMATION_KEYS = (
    "id", "nom", "prenom", "typo",
    "fpi", "fphi", "certif", "carte_pro", "badge_date_expiration",
    "email_envoye_fpi", "email_envoye_fphi", "email_envoye_certif", "email_envoye_carte_pro",
    "email_envoye_fpi2", "email_envoye_fpi3",
    "email_envoye_fphi2", "email_envoye_fphi3",
    "email_envoye_certif2", "email_envoye_certif3",
    "email_envoye_carte_pro2", "email_envoye_carte_pro3",
    "contact_id",
)

_BADGE_KEYS = (
    "id", "nom", "prenom", "numeroBadge", "numeroDemande",
    "etat", "dateSoumission", "dateFinAccordee",
    "dateNaissance", "email", "entreprise",
    "email_envoye_badge_expire", "numAA",
)

_AGENT_KEYS = (
    "id", "nom", "prenom", "mail", "tel1", "tel2",
    "date_inscription", "numero_salarie", "ville",
    "planete_id",
)


def _pick(d: dict, keys: tuple) -> dict:
    return {k: d[k] for k in keys if k in d}


class SupabaseClient:
    BASE_URL = "https://nhxzumcbqlyjumdirpax.supabase.co/rest/v1"

    def __init__(self, service_key: str):
        self._init_key = service_key

    def _key(self) -> str:
        return self._init_key or os.environ.get("SUPABASE_SERVICE_KEY", "")

    def _headers(self) -> dict[str, str]:
        k = self._key()
        return {
            "apikey": k,
            "Authorization": f"Bearer {k}",
            "Content-Type": "application/json",
        }

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        key = self._key()
        if not key:
            return {"error": "SUPABASE_SERVICE_KEY manquante"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}{path}",
                    headers=self._headers(),
                    params=params,
                )
                response.raise_for_status()
                return {"data": response.json()}
            except httpx.HTTPStatusError as e:
                return {"error": f"Erreur Supabase {e.response.status_code}", "details": e.response.text[:300]}
            except Exception as e:
                return {"error": "Erreur interne client", "details": str(e)}

    async def search_formation(self, nom: str, prenom: str = "") -> dict:
        params = {"select": "*", "nom": f"ilike.%{nom}%"}
        if prenom:
            params["prenom"] = f"ilike.%{prenom}%"
        result = await self._get("/formation", params)
        if "error" in result:
            return result
        rows = result["data"]
        return {"count": len(rows), "formations": [_pick(r, _FORMATION_KEYS) for r in rows]}

    async def get_formation_by_id(self, formation_id: int) -> dict:
        result = await self._get(f"/formation?id=eq.{formation_id}")
        if "error" in result:
            return result
        rows = result["data"]
        if not rows:
            return {"error": "Formation non trouvée"}
        return _pick(rows[0], _FORMATION_KEYS)

    async def list_formations(self, limit: int = 50, offset: int = 0, typo: str = "") -> dict:
        params: dict[str, Any] = {"select": "*", "limit": limit, "offset": offset, "order": "nom.asc"}
        if typo:
            params["typo"] = f"eq.{typo}"
        result = await self._get("/formation", params)
        if "error" in result:
            return result
        rows = result["data"]
        return {"count": len(rows), "formations": [_pick(r, _FORMATION_KEYS) for r in rows]}

    async def get_expired(self, date_ref: str | None = None) -> dict:
        today = date_ref or date.today().isoformat()
        or_clause = f"certif.lt.{today},fpi.lt.{today},fphi.lt.{today},carte_pro.lt.{today},badge_date_expiration.lt.{today}"
        params = {"select": "*", "or": f"({or_clause})"}
        result = await self._get("/formation", params)
        if "error" in result:
            return result
        rows = result["data"]
        return {"count": len(rows), "date_ref": today, "formations": [_pick(r, _FORMATION_KEYS) for r in rows]}

    async def get_expiring_soon(self, days: int = 30) -> dict:
        today = date.today()
        end = (today + timedelta(days=days)).isoformat()
        today_str = today.isoformat()
        or_clause = (
            f"and(certif.gte.{today_str},certif.lte.{end}),"
            f"and(fpi.gte.{today_str},fpi.lte.{end}),"
            f"and(fphi.gte.{today_str},fphi.lte.{end}),"
            f"and(carte_pro.gte.{today_str},carte_pro.lte.{end}),"
            f"and(badge_date_expiration.gte.{today_str},badge_date_expiration.lte.{end})"
        )
        params = {"select": "*", "or": f"({or_clause})"}
        result = await self._get("/formation", params)
        if "error" in result:
            return result
        rows = result["data"]
        return {"count": len(rows), "days": days, "date_from": today_str, "date_to": end, "formations": [_pick(r, _FORMATION_KEYS) for r in rows]}

    async def get_compliance_stats(self) -> dict:
        today = date.today().isoformat()
        all_rows = await self._get("/formation?select=id")
        if "error" in all_rows:
            return all_rows
        total = len(all_rows["data"])
        expired = await self.get_expired(today)
        if "error" in expired:
            return expired
        return {
            "total_agents": total,
            "expired": expired["count"],
            "valid": total - expired["count"],
        }

    async def search_badge(self, numero: str = "", nom: str = "") -> dict:
        params: dict[str, Any] = {"select": "*"}
        if numero:
            params["numeroBadge"] = f"ilike.%{numero}%"
        if nom:
            params["nom"] = f"ilike.%{nom}%"
        result = await self._get("/badges_corsur", params)
        if "error" in result:
            return result
        rows = result["data"]
        return {"count": len(rows), "badges": [_pick(r, _BADGE_KEYS) for r in rows]}

    async def search_agent(self, nom: str, prenom: str = "") -> dict:
        params: dict[str, Any] = {"select": "*", "nom": f"ilike.%{nom}%"}
        if prenom:
            params["prenom"] = f"ilike.%{prenom}%"
        result = await self._get("/interim_contact_information", params)
        if "error" in result:
            return result
        rows = result["data"]
        return {"count": len(rows), "agents": [_pick(r, _AGENT_KEYS) for r in rows]}

    async def get_agent_full_profile(self, nom: str, prenom: str = "") -> dict:
        formation_result = await self.search_formation(nom, prenom)
        if "error" in formation_result:
            return formation_result
        badge_result = await self.search_badge(nom=nom)
        if "error" in badge_result:
            badge_result = {"badges": []}
        agent_result = await self.search_agent(nom, prenom)
        if "error" in agent_result:
            agent_result = {"agents": []}
        return {
            "formations": formation_result.get("formations", []),
            "badges": badge_result.get("badges", []),
            "agent_info": agent_result.get("agents", []),
        }

    async def get_typo_stats(self) -> dict:
        result = await self._get("/formation?select=typo")
        if "error" in result:
            return result
        rows = result["data"]
        counts: dict[str, int] = {}
        for r in rows:
            t = r.get("typo") or "N/A"
            counts[t] = counts.get(t, 0) + 1
        return {"typo_stats": [{"typo": k, "count": v} for k, v in sorted(counts.items())]}
