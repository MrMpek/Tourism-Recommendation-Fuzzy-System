"""
Hybrid Tourism Recommender System.
Integrates Mamdani Fuzzy Inference Engine + Fuzzy C-Means (FCM) Soft Personas + Catalog Matching.
Provides transparent Explainable AI (XAI) rationale for travel agencies and clients.
"""
from typing import Dict, List, Any, Optional
import numpy as np

from core.fuzzy_engine import FuzzyTourismEngine, DestinationArchetype
from core.fcm_clustering import FuzzyCMeansModel, generate_synthetic_tourist_dataset
from data.catalog_manager import CatalogManager
from data.feedback_manager import FeedbackManager


class HybridTourismRecommender:
    """
    Enterprise-ready Hybrid Tourism Recommender.
    Combines:
    1. Mamdani FIS: rule-based fuzzy reasoning and defuzzification
    2. FCM Clustering: soft behavioral clustering into tourist personas
    3. Multi-criteria matching: budget compatibility, duration fit, and activity alignment
    4. Adaptive Feedback Loop: incorporates user ratings to continuously refine recommendations
    """
    def __init__(self, catalog_path: Optional[str] = None):
        self.fuzzy_engine = FuzzyTourismEngine()
        self.catalog_mgr = CatalogManager(catalog_path)
        self.feedback_mgr = FeedbackManager()
        self.fcm_model = FuzzyCMeansModel(n_clusters=5, m=2.0)
        self._initialize_fcm()

    def _initialize_fcm(self):
        """Fits FCM on synthetic historical tourist dataset."""
        X_norm, _ = generate_synthetic_tourist_dataset(n_samples=350, random_state=42)
        self.fcm_model.fit(X_norm)

    def recommend(self, user_inputs: Dict[str, float], top_n: int = 5, country_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes complete recommendation pipeline.
        
        user_inputs schema:
            budget: float (€ total budget)
            climate: float (°C preferred temperature)
            duration: float (trip days)
            culture: float (0 - 10)
            adventure: float (0 - 10)
            relaxation: float (0 - 10)
            nightlife: float (0 - 10)
        """
        # Step 1: Fuzzify inputs
        fuzzified = self.fuzzy_engine.fuzzify_inputs(user_inputs)

        # Step 2: Mamdani Rule Evaluation & Defuzzification
        active_rules = self.fuzzy_engine.evaluate_rules(fuzzified)
        archetype_affinities = self.fuzzy_engine.compute_archetype_affinities(active_rules)

        # Step 3: FCM Soft Persona Profiling
        persona_profiling = self.fcm_model.predict_membership(user_inputs)

        # Step 4: Multi-Criteria Scoring for each Destination in Catalog
        destinations = self.catalog_mgr.get_all()
        scored_destinations = []

        total_budget = float(user_inputs.get("budget", 1000.0))
        duration_days = float(user_inputs.get("duration", 5.0))
        desired_temp = float(user_inputs.get("climate", 22.0))
        user_culture = float(user_inputs.get("culture", 5.0))
        user_adventure = float(user_inputs.get("adventure", 5.0))
        user_relaxation = float(user_inputs.get("relaxation", 5.0))
        user_nightlife = float(user_inputs.get("nightlife", 5.0))

        for dest in destinations:
            # Country filtering if requested
            if country_filter and country_filter != "Όλες" and dest.get("country") != country_filter:
                continue

            # A. Archetype Fuzzy Match (0 to 100)
            primary_arch = dest.get("archetype")
            secondary_arch = dest.get("secondary_archetype")
            arch_score = archetype_affinities.get(primary_arch, 50.0)
            if secondary_arch and secondary_arch in archetype_affinities:
                arch_score = 0.75 * arch_score + 0.25 * archetype_affinities[secondary_arch]

            # B. Budget Compatibility (Fuzzy tolerance)
            # Estimated total cost for this trip = daily_cost * duration
            est_cost = dest.get("avg_daily_cost", 120.0) * duration_days
            cost_diff = est_cost - total_budget
            if cost_diff <= 0:
                # Within budget: full score
                budget_score = 100.0
            else:
                # Over budget: degrade smoothly
                pct_over = cost_diff / total_budget
                budget_score = max(0.0, 100.0 * (1.0 - 1.5 * pct_over))

            # C. Duration Compatibility
            min_d, max_d = dest.get("optimal_duration_days", [3, 7])
            if min_d <= duration_days <= max_d:
                duration_score = 100.0
            elif duration_days < min_d:
                duration_score = max(40.0, 100.0 - (min_d - duration_days) * 20.0)
            else:
                duration_score = max(50.0, 100.0 - (duration_days - max_d) * 10.0)

            # D. Climate Compatibility (Temperature proximity)
            dest_temp = dest.get("typical_temperature_c", 22.0)
            temp_diff = abs(dest_temp - desired_temp)
            # Gaussian-like temperature satisfaction
            climate_score = max(0.0, 100.0 * np.exp(- (temp_diff ** 2) / (2 * (6.0 ** 2))))

            # E. Activity Vector Alignment
            dest_scores = dest.get("scores", {})
            diff_culture = abs(user_culture - dest_scores.get("culture", 5.0))
            diff_adventure = abs(user_adventure - dest_scores.get("adventure", 5.0))
            diff_relaxation = abs(user_relaxation - dest_scores.get("relaxation", 5.0))
            diff_nightlife = abs(user_nightlife - dest_scores.get("nightlife", 5.0))
            avg_diff = (diff_culture + diff_adventure + diff_relaxation + diff_nightlife) / 4.0
            activity_score = max(0.0, 100.0 - (avg_diff * 10.0))

            # F. Final Weighted Aggregation (Master Score)
            base_score = (
                0.35 * arch_score +
                0.20 * budget_score +
                0.20 * activity_score +
                0.15 * climate_score +
                0.10 * duration_score
            )

            # G. Adaptive Feedback Loop Adjustment
            fb_stats = self.feedback_mgr.get_destination_feedback_stats(dest.get("id", ""))
            fb_delta = fb_stats.get("feedback_delta", 0.0)
            final_score = round(min(100.0, max(0.0, base_score + fb_delta)), 1)

            # Explainable AI (XAI) rationale synthesis
            rationale_reasons = []
            if arch_score >= 70:
                rationale_reasons.append(f"Εξαιρετική αντιστοίχιση με τον τύπο προορισμού '{primary_arch}' (Fuzzy: {round(arch_score, 1)}%)")
            if budget_score >= 85:
                rationale_reasons.append(f"Πλήρης κάλυψη προϋπολογισμού (Εκτιμώμενο κόστος: ~{int(est_cost)}€ έναντι {int(total_budget)}€)")
            elif budget_score < 50:
                rationale_reasons.append(f"Προσοχή στο budget: Υπέρβαση (~{int(est_cost)}€ έναντι {int(total_budget)}€)")
            if climate_score >= 75:
                rationale_reasons.append(f"Ιδανική θερμοκρασία ({dest_temp}°C έναντι επιθυμητής {int(desired_temp)}°C)")
            if activity_score >= 75:
                rationale_reasons.append("Υψηλή αρμονία με τις επιθυμητές δραστηριότητες")
            if fb_delta > 0:
                rationale_reasons.append(f"📈 Ενισχυμένο από θετική ανάδραση χρηστών (+{fb_delta}% από {fb_stats['count']} κριτικές)")
            elif fb_delta < 0:
                rationale_reasons.append(f"📉 Προσαρμογή από προηγούμενη αρνητική ανάδραση ({fb_delta}%)")

            scored_destinations.append({
                "destination": dest,
                "final_score": final_score,
                "base_score": round(base_score, 1),
                "feedback_stats": fb_stats,
                "component_scores": {
                    "archetype_fuzzy": round(arch_score, 1),
                    "budget_compatibility": round(budget_score, 1),
                    "activity_alignment": round(activity_score, 1),
                    "climate_match": round(climate_score, 1),
                    "duration_fit": round(duration_score, 1),
                    "feedback_adjustment": fb_delta
                },
                "estimated_trip_cost": int(est_cost),
                "rationale": rationale_reasons
            })

        # Sort descending by final match score
        scored_destinations.sort(key=lambda x: x["final_score"], reverse=True)
        top_recommendations = scored_destinations[:top_n]

        return {
            "user_inputs": user_inputs,
            "fuzzified_inputs": fuzzified,
            "active_fuzzy_rules": active_rules[:6],
            "archetype_affinities": archetype_affinities,
            "fcm_profiling": persona_profiling,
            "recommendations": top_recommendations
        }

    def record_feedback(self, destination_id: str, destination_name: str, user_query: Dict[str, float], rating: int, accepted: bool, comment: str = "") -> Dict[str, Any]:
        """Records user feedback and triggers adaptive weighting."""
        return self.feedback_mgr.record_feedback(destination_id, destination_name, user_query, rating, accepted, comment)
