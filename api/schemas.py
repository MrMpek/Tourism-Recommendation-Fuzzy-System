"""
Pydantic Data Schemas for the Tourism Recommender System.
Provides validation and typed contracts for API and UI layers.
"""
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field


class UserPreferencesRequest(BaseModel):
    """Traveler input preferences."""
    budget: float = Field(..., ge=100.0, le=10000.0, description="Total budget in Euros")
    climate: float = Field(..., ge=-10.0, le=45.0, description="Preferred average temperature in Celsius")
    duration: float = Field(..., ge=1.0, le=30.0, description="Duration of travel in days")
    culture: float = Field(..., ge=0.0, le=10.0, description="Interest in cultural & historical sites (0-10)")
    adventure: float = Field(..., ge=0.0, le=10.0, description="Interest in adventure, hiking & outdoors (0-10)")
    relaxation: float = Field(..., ge=0.0, le=10.0, description="Interest in relaxation, beaches & spa (0-10)")
    nightlife: float = Field(..., ge=0.0, le=10.0, description="Interest in nightlife, clubs & vibrant city life (0-10)")
    country_filter: Optional[str] = Field("Όλες", description="Optional filter by country")


class DestinationScoreBreakdown(BaseModel):
    archetype_fuzzy: float
    budget_compatibility: float
    activity_alignment: float
    climate_match: float
    duration_fit: float


class RecommendedDestination(BaseModel):
    destination_id: str
    name: str
    country: str
    region: str
    archetype: str
    final_score: float
    estimated_trip_cost: int
    agency_package: Optional[str] = None
    component_scores: DestinationScoreBreakdown
    rationale: List[str]
    image_url: Optional[str] = None


class RecommendationResponse(BaseModel):
    dominant_persona: str
    dominant_persona_pct: float
    fcm_persona_weights: Dict[str, float]
    active_fuzzy_rules_count: int
    top_recommendations: List[RecommendedDestination]
