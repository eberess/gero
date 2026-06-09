# geroAds

Module de monétisation contextuelle pour la plateforme humanoïde **Unitree G1** au Terminal 2F de Roissy-CDG. Transforme le robot d'orientation en hub de services proactif via du **Native Advertising conversationnel**.

## Architecture

```
geroAds/
├── backend/               # FastAPI — moteur d'enchères et API REST
│   ├── app/
│   │   ├── main.py        # Routes publiques /api/ads/*
│   │   ├── llm.py         # Routes LLM /llm/ads (pour le robot)
│   │   ├── models.py      # Pydantic + SQLAlchemy
│   │   ├── database.py    # SQLite
│   │   └── services/
│   │       ├── auction_engine.py  # Enchères contextuelles
│   │       ├── organic_index.py   # Index gratuit des commerces
│   │       └── booster.py         # Boost Artisans & Niche (20%)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/              # Next.js — Gero Business Portal
│   ├── src/app/           # Dashboard, gestion campagnes
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml     # Orchestration backend + frontend
└── README.md
```

## Quick Start

```bash
docker compose up --build
```

- **API** : http://localhost:8000
- **Docs** : http://localhost:8000/docs
- **Portal** : http://localhost:3000

## Endpoints API

| Méthode | Route | Rôle |
|---------|-------|------|
| `POST` | `/api/ads/recommend` | Recommandation contextuelle |
| `POST` | `/api/ads/campaign` | Créer une campagne |
| `GET` | `/api/ads/campaigns` | Lister les campagnes |
| `GET` | `/api/ads/campaign/{id}` | Détail d'une campagne |
| `POST` | `/api/shops` | Ajouter un commerce |
| `GET` | `/api/shops` | Lister les commerces |
| `POST` | `/llm/ads` | Version simplifiée pour le LLM |

## Algorithme de recommandation

1. **Indexation organique** (gratuit) — Tous les commerces T2F, priorité géographique
2. **Enchères contextuelles** (premium) — Campagnes payantes au plus offrant
3. **Boost Artisans** (20% réservé) — Découverte de l'artisanat local

Le ciblage est exclusivement contextuel et anonyme (langue, heure, zone d'embarquement) — aucun profiling biométrique. Conforme RGPD.
