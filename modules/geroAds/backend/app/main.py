from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import init_db, get_db
from app.models import (
    CampaignCreate, CampaignOut, CampaignDB, CampaignStatus,
    ShopCreate, ShopOut, ShopDB,
    RecommendationRequest, RecommendationResponse, AdRecommendation,
    LoginRequest, TokenResponse, UserOut, UserDB, UserRole,
)
from app.services.organic_index import OrganicIndex
from app.services.auction_engine import AuctionEngine
from app.services.booster import ArtisanBooster
from app.auth import hash_password, verify_password, create_access_token, get_current_user, require_role
from app.llm import router as llm_router
from datetime import datetime
from typing import List

app = FastAPI(
    title="geroAds API",
    description="Moteur de monétisation contextuelle pour Unitree G1 — Terminal 2F CDG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm_router)


def seed_defaults(db: Session):
    if db.query(UserDB).count() > 0:
        return
    db.add_all([
        UserDB(
            email="admin@adp.fr",
            password_hash=hash_password("admin123"),
            company="Aéroports de Paris",
            role=UserRole.ADMIN,
        ),
        UserDB(
            email="contact@paul bakery.fr",
            password_hash=hash_password("merchant123"),
            company="Paul Boulangerie",
            role=UserRole.MERCHANT,
            shop_name="Paul CDG T2F",
        ),
        UserDB(
            email="contact@ladycafe.fr",
            password_hash=hash_password("merchant123"),
            company="Lady Café",
            role=UserRole.MERCHANT,
            shop_name="Lady Café T2F",
        ),
        UserDB(
            email="contact@relay.fr",
            password_hash=hash_password("merchant123"),
            company="Relay",
            role=UserRole.MERCHANT,
            shop_name="Relay T2F Central",
        ),
    ])
    db.commit()


@app.on_event("startup")
def on_startup():
    init_db()
    db = next(get_db())
    seed_defaults(db)
    db.close()


@app.get("/")
def read_root():
    return {"service": "geroAds", "status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe invalide")
    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(
        access_token=token,
        user=UserOut(
            id=user.id,
            email=user.email,
            company=user.company,
            role=user.role,
            shop_name=user.shop_name,
        ),
    )


@app.get("/api/auth/me", response_model=UserOut)
def me(current_user: UserDB = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        company=current_user.company,
        role=current_user.role,
        shop_name=current_user.shop_name,
    )


@app.post("/api/ads/recommend", response_model=RecommendationResponse)
def recommend_ads(req: RecommendationRequest, db: Session = Depends(get_db)):
    engine = AuctionEngine(db)
    organic = OrganicIndex(db)
    booster = ArtisanBooster(db)

    sponsored = engine.find_best_ads(req.intent, req.zone, req.lang, limit=2)
    organic_results = organic.search(req.intent, req.zone, req.lang, limit=3)

    total_slots = 3
    sponsored_count = len(sponsored)
    organic_count = min(len(organic_results), total_slots - sponsored_count)

    current_hour = datetime.utcnow().hour
    is_off_peak = current_hour < 10 or current_hour > 14

    results = []

    for s in sponsored[:2]:
        c = s["campaign"]
        tagline = f"Offre spéciale chez {c.shop_name} — {c.keywords[:80]}" if c.keywords else f"Découvrez {c.shop_name}"
        results.append(AdRecommendation(
            shop_name=c.shop_name,
            advertiser=c.advertiser,
            tagline=tagline,
            is_sponsored=True,
        ))
        engine.record_impression(c.id, req.intent, req.zone, req.lang)

    for o in organic_results[:organic_count]:
        results.append(AdRecommendation(**o))

    if is_off_peak and len(results) < total_slots:
        boost = booster.boost(req.zone, limit=1)
        results.extend([AdRecommendation(**b) for b in boost])

    return RecommendationResponse(recommendations=results[:total_slots])


@app.post("/api/ads/campaign", response_model=CampaignOut)
def create_campaign(
    c: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role(UserRole.ADMIN, UserRole.MERCHANT)),
):
    advertiser = c.advertiser if current_user.role == UserRole.ADMIN else current_user.company
    shop_name = c.shop_name if current_user.role == UserRole.ADMIN else (current_user.shop_name or c.shop_name)
    campaign = CampaignDB(
        advertiser=advertiser,
        shop_name=shop_name,
        zone=c.zone.value,
        keywords=",".join(c.keywords),
        budget_cents=c.budget_cents,
        bid_cents=c.bid_cents,
        strategy=c.strategy.value,
        status=CampaignStatus.ACTIVE,
        daily_max_cents=c.daily_max_cents,
        starts_at=c.starts_at,
        ends_at=c.ends_at,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@app.get("/api/ads/campaigns", response_model=List[CampaignOut])
def list_campaigns(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role(UserRole.ADMIN, UserRole.MERCHANT)),
):
    query = db.query(CampaignDB)
    if current_user.role == UserRole.MERCHANT and current_user.shop_name:
        query = query.filter(CampaignDB.shop_name == current_user.shop_name)
    return query.order_by(CampaignDB.created_at.desc()).all()


@app.get("/api/ads/campaign/{campaign_id}", response_model=CampaignOut)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role(UserRole.ADMIN, UserRole.MERCHANT)),
):
    c = db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campagne introuvable")
    if current_user.role == UserRole.MERCHANT and current_user.shop_name and c.shop_name != current_user.shop_name:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return c


@app.get("/api/ads/stats", response_model=dict)
def get_stats(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role(UserRole.ADMIN)),
):
    from app.models import ImpressionDB
    total_campaigns = db.query(CampaignDB).count()
    active_campaigns = db.query(CampaignDB).filter(CampaignDB.status == CampaignStatus.ACTIVE).count()
    total_impressions = db.query(ImpressionDB).count()
    total_budget = db.query(CampaignDB).with_entities(CampaignDB.budget_cents).all()
    total_budget_sum = sum(b[0] for b in total_budget) / 100 if total_budget else 0
    return {
        "total_campaigns": total_campaigns,
        "active_campaigns": active_campaigns,
        "total_impressions": total_impressions,
        "total_budget_eur": round(total_budget_sum, 2),
    }


@app.get("/api/ads/merchant/stats", response_model=dict)
def get_merchant_stats(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role(UserRole.MERCHANT)),
):
    from app.models import ImpressionDB
    query = db.query(CampaignDB)
    if current_user.shop_name:
        query = query.filter(CampaignDB.shop_name == current_user.shop_name)
    campaigns = query.all()
    total_budget = sum(c.budget_cents for c in campaigns) / 100
    active = sum(1 for c in campaigns if c.status == CampaignStatus.ACTIVE)
    campaign_ids = [c.id for c in campaigns]
    impressions = 0
    if campaign_ids:
        impressions = db.query(ImpressionDB).filter(ImpressionDB.campaign_id.in_(campaign_ids)).count()
    return {
        "total_campaigns": len(campaigns),
        "active_campaigns": active,
        "total_impressions": impressions,
        "total_budget_eur": round(total_budget, 2),
    }


@app.post("/api/shops", response_model=ShopOut)
def create_shop(
    s: ShopCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role(UserRole.ADMIN)),
):
    shop = ShopDB(
        name=s.name,
        zone=s.zone.value,
        category=s.category,
        description=s.description,
        tags=",".join(s.tags),
        lat=s.lat,
        lon=s.lon,
        is_artisan=s.is_artisan,
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


@app.get("/api/shops", response_model=List[ShopOut])
def list_shops(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role(UserRole.ADMIN, UserRole.MERCHANT)),
):
    return db.query(ShopDB).all()


@app.get("/api/users", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role(UserRole.ADMIN)),
):
    users = db.query(UserDB).all()
    return [
        UserOut(id=u.id, email=u.email, company=u.company, role=u.role, shop_name=u.shop_name)
        for u in users
    ]
