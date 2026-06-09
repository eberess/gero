from sqlalchemy.orm import Session
from app.models import ShopDB
from typing import List, Dict


class OrganicIndex:
    def __init__(self, db: Session):
        self.db = db

    def search(self, intent: str, zone: str, lang: str, limit: int = 3) -> List[Dict]:
        query = self.db.query(ShopDB)
        if zone and zone != "all":
            query = query.filter(ShopDB.zone == zone)
        shops = query.limit(limit).all()
        return [
            {
                "shop_name": s.name,
                "advertiser": s.name,
                "tagline": s.description or f"{s.category} à proximité",
                "is_sponsored": False,
            }
            for s in shops
        ]
