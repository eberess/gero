from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import CampaignDB, CampaignStatus, BidStrategy, ImpressionDB
from datetime import datetime, date
from typing import List, Dict, Optional


class AuctionEngine:
    def __init__(self, db: Session):
        self.db = db

    def find_best_ads(self, intent: str, zone: str, lang: str, limit: int = 2) -> List[Dict]:
        now = datetime.utcnow()
        campaigns = (
            self.db.query(CampaignDB)
            .filter(
                CampaignDB.status == CampaignStatus.ACTIVE,
                CampaignDB.starts_at <= now,
                (CampaignDB.ends_at.is_(None) | (CampaignDB.ends_at >= now)),
                (CampaignDB.budget_cents > 0),
            )
            .all()
        )
        scored = []
        for c in campaigns:
            bid = c.bid_cents
            if c.strategy == BidStrategy.FLASH:
                bid *= 2
            if c.daily_max_cents > 0:
                today_start = datetime.combine(date.today(), datetime.min.time())
                spent_today = (
                    self.db.query(func.sum(ImpressionDB.campaign_id))
                    .filter(
                        ImpressionDB.campaign_id == c.id,
                        ImpressionDB.served_at >= today_start,
                    )
                    .scalar()
                ) or 0
                if spent_today >= c.daily_max_cents:
                    continue
            if zone and zone != "all" and c.zone not in ("all", zone):
                continue
            scored.append({"campaign": c, "score": bid})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    def record_impression(self, campaign_id: int, intent: str, zone: str, lang: str):
        impression = ImpressionDB(
            campaign_id=campaign_id,
            intent=intent,
            zone=zone,
            lang=lang,
        )
        self.db.add(impression)
        self.db.commit()
