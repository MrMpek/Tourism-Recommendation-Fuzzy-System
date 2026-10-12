"""
Catalog Manager for Tourism Destinations and Agency Packages.
Supports loading, filtering, extending, and persisting travel agency inventory.
"""
import json
import os
from typing import List, Dict, Any, Optional
import pandas as pd


class CatalogManager:
    """Manages destination data for both the Fuzzy Recommender and travel agencies."""
    DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "destinations.json")

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or self.DEFAULT_PATH
        self.destinations: List[Dict[str, Any]] = []
        self.load()

    def load(self) -> List[Dict[str, Any]]:
        """Loads destinations from JSON storage."""
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.destinations = json.load(f)
        else:
            self.destinations = []
        return self.destinations

    def save(self):
        """Persists destinations back to JSON file."""
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.destinations, f, ensure_ascii=False, indent=2)

    def get_all(self) -> List[Dict[str, Any]]:
        return self.destinations

    def get_by_id(self, dest_id: str) -> Optional[Dict[str, Any]]:
        for d in self.destinations:
            if d.get("id") == dest_id:
                return d
        return None

    def add_destination(self, dest_dict: Dict[str, Any]) -> bool:
        """Adds or updates a destination (useful for agencies adding their own packages)."""
        existing = self.get_by_id(dest_dict.get("id", ""))
        if existing:
            self.destinations.remove(existing)
        self.destinations.append(dest_dict)
        self.save()
        return True

    def to_dataframe(self) -> pd.DataFrame:
        """Flattens destination records into a tabular pandas DataFrame."""
        flat_records = []
        for d in self.destinations:
            flat = {
                "id": d["id"],
                "name": d["name"],
                "country": d["country"],
                "region": d["region"],
                "archetype": d["archetype"],
                "avg_daily_cost": d["avg_daily_cost"],
                "budget_tier": d["budget_tier"],
                "min_days": d["optimal_duration_days"][0],
                "max_days": d["optimal_duration_days"][1],
                "typical_temp": d["typical_temperature_c"],
                "climate_label": d["climate_label"],
                "culture_score": d["scores"]["culture"],
                "adventure_score": d["scores"]["adventure"],
                "relaxation_score": d["scores"]["relaxation"],
                "nightlife_score": d["scores"]["nightlife"],
                "agency_package": d.get("agency_package", "")
            }
            flat_records.append(flat)
        return pd.DataFrame(flat_records)
