from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RecommendationRequest, RecommendationResponse, AdRecommendation
from app.services.organic_index import OrganicIndex
from app.services.auction_engine import AuctionEngine
from app.services.booster import ArtisanBooster
from datetime import datetime

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/ads", response_model=RecommendationResponse)
def llm_recommend(
    intent: str = "waiting",
    zone: str = "all",
    lang: str = "fr",
    db: Session = Depends(get_db),
):
    req = RecommendationRequest(intent=intent, zone=zone, lang=lang)
    engine = AuctionEngine(db)
    organic = OrganicIndex(db)
    booster = ArtisanBooster(db)

    sponsored = engine.find_best_ads(req.intent, req.zone, req.lang, limit=1)
    organic_results = organic.search(req.intent, req.zone, req.lang, limit=2)

    results = []
    for s in sponsored[:1]:
        c = s["campaign"]
        tagline = f"Promo : {c.keywords[:100]}" if c.keywords else f"Découvrez {c.shop_name}"
        results.append(AdRecommendation(
            shop_name=c.shop_name,
            advertiser=c.advertiser,
            tagline=tagline,
            is_sponsored=True,
        ))
        engine.record_impression(c.id, req.intent, req.zone, req.lang)

    for o in organic_results[:2]:
        results.append(AdRecommendation(**o))

    if len(results) < 3:
        boost = booster.boost(req.zone, limit=1)
        results.extend([AdRecommendation(**b) for b in boost])

    return RecommendationResponse(recommendations=results[:3])
