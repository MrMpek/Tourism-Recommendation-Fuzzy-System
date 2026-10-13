"""
Persona Mapping Module for FuzzyTravel AI.
Connects Fuzzy C-Means (FCM) traveler personas to destination archetypes
via a calibrated preference matrix W[j][archetype].
Computes persona-archetype affinity scores for personalized destination recommendations.
"""
from typing import Dict, List, Any
from core.fuzzy_engine import DestinationArchetype

# Persona names corresponding to TouristPersona definitions
# Maps each FCM Persona to its inherent preference weight for each Destination Archetype
PERSONA_ARCHETYPE_MATRIX: Dict[str, Dict[str, float]] = {
    "Cultural & Heritage Explorer": {
        DestinationArchetype.CULTURAL_HERITAGE: 1.00,
        DestinationArchetype.ISLAND_RELAXATION: 0.35,
        DestinationArchetype.MOUNTAIN_ADVENTURE: 0.30,
        DestinationArchetype.LUXURY_ESCORT: 0.50,
        DestinationArchetype.VIBRANT_NIGHTLIFE: 0.60,
        DestinationArchetype.EXOTIC_EXPLORATION: 0.40,
    },
    "Luxury & Wellness Relaxer": {
        DestinationArchetype.CULTURAL_HERITAGE: 0.45,
        DestinationArchetype.ISLAND_RELAXATION: 0.90,
        DestinationArchetype.MOUNTAIN_ADVENTURE: 0.20,
        DestinationArchetype.LUXURY_ESCORT: 1.00,
        DestinationArchetype.VIBRANT_NIGHTLIFE: 0.45,
        DestinationArchetype.EXOTIC_EXPLORATION: 0.50,
    },
    "Budget Backpacker & Youth Nomad": {
        DestinationArchetype.CULTURAL_HERITAGE: 0.60,
        DestinationArchetype.ISLAND_RELAXATION: 0.50,
        DestinationArchetype.MOUNTAIN_ADVENTURE: 0.85,
        DestinationArchetype.LUXURY_ESCORT: 0.10,
        DestinationArchetype.VIBRANT_NIGHTLIFE: 0.85,
        DestinationArchetype.EXOTIC_EXPLORATION: 0.90,
    },
    "Alpine & Nature Adventure Seeker": {
        DestinationArchetype.CULTURAL_HERITAGE: 0.30,
        DestinationArchetype.ISLAND_RELAXATION: 0.25,
        DestinationArchetype.MOUNTAIN_ADVENTURE: 1.00,
        DestinationArchetype.LUXURY_ESCORT: 0.20,
        DestinationArchetype.VIBRANT_NIGHTLIFE: 0.20,
        DestinationArchetype.EXOTIC_EXPLORATION: 0.80,
    },
    "Cosmopolitan & Nightlife Vibe": {
        DestinationArchetype.CULTURAL_HERITAGE: 0.70,
        DestinationArchetype.ISLAND_RELAXATION: 0.50,
        DestinationArchetype.MOUNTAIN_ADVENTURE: 0.15,
        DestinationArchetype.LUXURY_ESCORT: 0.60,
        DestinationArchetype.VIBRANT_NIGHTLIFE: 1.00,
        DestinationArchetype.EXOTIC_EXPLORATION: 0.30,
    },
}


def compute_persona_affinity(persona_memberships: List[Dict[str, Any]], archetype: str) -> float:
    """
    Computes persona affinity for a given destination archetype:
        persona_affinity(archetype) = sum_j (u_j * W[j][archetype])
    where u_j is the membership degree of the traveler in persona j,
    and W[j][archetype] is the affinity weight from PERSONA_ARCHETYPE_MATRIX.
    Returns a normalized affinity value in [0.0, 1.0].
    """
    if not archetype:
        return 0.5

    total_affinity = 0.0
    total_weight = 0.0
    for p in persona_memberships:
        p_name = p.get("name")
        u_j = float(p.get("membership_degree", 0.0))
        weights = PERSONA_ARCHETYPE_MATRIX.get(p_name, {})
        w_arch = weights.get(archetype, 0.5)
        total_affinity += u_j * w_arch
        total_weight += u_j

    if total_weight > 0.0:
        return total_affinity / total_weight
    return 0.5
