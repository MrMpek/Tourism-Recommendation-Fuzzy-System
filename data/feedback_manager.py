"""
Feedback Manager for Tourism Recommendations.
Records user ratings, acceptance/rejection of proposed destinations,
and provides adaptive score adjustments to close the feedback loop.
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class FeedbackManager:
    """Manages user feedback, persistent storage, and adaptive score adjustments."""
    DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "feedback_history.json")

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or self.DEFAULT_PATH
        self.feedback_entries: List[Dict[str, Any]] = []
        self.load()

    def load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.feedback_entries = json.load(f)
            except Exception:
                self.feedback_entries = []
        else:
            self.feedback_entries = []

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.feedback_entries, f, ensure_ascii=False, indent=2)

    def record_feedback(self, destination_id: str, destination_name: str, user_query: Dict[str, float], rating: int, accepted: bool, comment: str = "") -> Dict[str, Any]:
        """
        Records a user feedback event.
        rating: 1 to 5 stars
        accepted: True if user would book/visit, False otherwise
        """
        entry = {
            "id": f"fb_{len(self.feedback_entries) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "destination_id": destination_id,
            "destination_name": destination_name,
            "user_query": user_query,
            "rating": rating,
            "accepted": accepted,
            "comment": comment
        }
        self.feedback_entries.append(entry)
        self.save()
        return entry

    def get_destination_feedback_stats(self, destination_id: str) -> Dict[str, Any]:
        """Calculates historical feedback statistics for a specific destination."""
        dest_entries = [e for e in self.feedback_entries if e.get("destination_id") == destination_id]
        if not dest_entries:
            return {"count": 0, "avg_rating": 3.0, "acceptance_rate": 0.5, "feedback_delta": 0.0}

        count = len(dest_entries)
        avg_rating = sum(e["rating"] for e in dest_entries) / count
        acceptance_rate = sum(1 for e in dest_entries if e["accepted"]) / count

        # Adaptive feedback delta: [-10.0, +10.0] points to adjust match score
        # Rating 3 is neutral (delta 0). Rating 5 gives up to +8, Rating 1 gives -8.
        # Acceptance rate > 0.5 adds up to +2, < 0.5 subtracts up to -2.
        rating_delta = (avg_rating - 3.0) * 4.0
        acceptance_delta = (acceptance_rate - 0.5) * 4.0
        total_delta = max(-10.0, min(10.0, rating_delta + acceptance_delta))

        return {
            "count": count,
            "avg_rating": round(avg_rating, 2),
            "acceptance_rate": round(acceptance_rate * 100.0, 1),
            "feedback_delta": round(total_delta, 1)
        }

    def get_overall_summary(self) -> Dict[str, Any]:
        """Returns overall analytics across all feedback entries."""
        if not self.feedback_entries:
            return {"total_feedbacks": 0, "avg_rating": 0.0, "acceptance_rate": 0.0}

        total = len(self.feedback_entries)
        avg_rating = sum(e["rating"] for e in self.feedback_entries) / total
        acceptance_rate = (sum(1 for e in self.feedback_entries if e["accepted"]) / total) * 100.0

        return {
            "total_feedbacks": total,
            "avg_rating": round(avg_rating, 2),
            "acceptance_rate": round(acceptance_rate, 1)
        }
