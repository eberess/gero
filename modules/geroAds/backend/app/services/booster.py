from sqlalchemy.orm import Session
from app.models import ShopDB
from typing import List, Dict


class ArtisanBooster:
    RESERVED_RATIO = 0.2

    def __init__(self, db: Session):
        self.db = db

    def boost(self, zone: str, limit: int = 1) -> List[Dict]:
        query = self.db.query(ShopDB).filter(ShopDB.is_artisan == True)
        if zone and zone != "all":
            query = query.filter(ShopDB.zone == zone)
        artisans = query.limit(limit).all()
        return [
            {
                "shop_name": s.name,
                "advertiser": s.name,
                "tagline": f"Découvrez l'artisanat local — {s.description}" if s.description else "Artisan local à découvrir",
                "is_sponsored": False,
            }
            for s in artisans
        ]
