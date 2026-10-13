"""
Mamdani Fuzzy Inference System for Tourism Recommendations.
Implements fuzzification, fuzzy rule evaluation (min/max), aggregation, and centroid defuzzification.
Comprehensive expert rule base of 36 rules covering all archetypes with full linguistic coverage.
"""
from typing import Dict, List, Any, Tuple
import numpy as np
from core.membership import LinguisticVariable, trapezoidal, triangular


class DestinationArchetype:
    CULTURAL_HERITAGE = "Cultural & Heritage City"
    ISLAND_RELAXATION = "Coastal & Island Relaxation"
    MOUNTAIN_ADVENTURE = "Alpine & Mountain Adventure"
    LUXURY_ESCORT = "Luxury & Premium Wellness"
    VIBRANT_NIGHTLIFE = "Vibrant Urban & Entertainment"
    EXOTIC_EXPLORATION = "Exotic & Tropical Explorer"


class FuzzyRule:
    """Represents a fuzzy IF-THEN rule with antecedent conditions and consequent conclusions."""
    def __init__(self, rule_id: str, antecedent: Dict[str, str], consequent: Dict[str, str], weight: float = 1.0, description: str = ""):
        self.rule_id = rule_id
        self.antecedent = antecedent   # e.g., {"budget": "Low", "duration": "Short", "adventure": "High"}
        self.consequent = consequent   # e.g., {"suitability": "High", "archetype": DestinationArchetype.MOUNTAIN_ADVENTURE}
        self.weight = weight
        self.description = description


class FuzzyTourismEngine:
    """
    Expert System Inference Engine based on Mamdani Fuzzy Logic.
    Calculates suitability scores for tourism destinations and destination archetypes.
    """
    def __init__(self):
        # 1. Input Variable: Budget (€ total per person) [Universe: 100 to 5000 €]
        self.var_budget = LinguisticVariable("budget", (100.0, 5000.0), "€")
        self.var_budget.add_trapezoidal("Low", 100.0, 100.0, 500.0, 900.0)
        self.var_budget.add_triangular("Medium", 650.0, 1500.0, 2500.0)
        self.var_budget.add_trapezoidal("High", 2000.0, 3200.0, 5000.0, 5000.0)

        # 2. Input Variable: Climate / Temperature (°C) [Universe: -10 to 45 °C]
        self.var_climate = LinguisticVariable("climate", (-10.0, 45.0), "°C")
        self.var_climate.add_trapezoidal("Cold", -10.0, -10.0, 8.0, 15.0)
        self.var_climate.add_triangular("Mild", 12.0, 20.0, 27.0)
        self.var_climate.add_trapezoidal("Warm", 24.0, 30.0, 45.0, 45.0)

        # 3. Input Variable: Duration (Days) [Universe: 1 to 30 days]
        self.var_duration = LinguisticVariable("duration", (1.0, 30.0), "days")
        self.var_duration.add_trapezoidal("Short", 1.0, 1.0, 3.0, 5.0)
        self.var_duration.add_triangular("Medium", 4.0, 7.0, 12.0)
        self.var_duration.add_trapezoidal("Long", 10.0, 15.0, 30.0, 30.0)

        # 4. Input Variables: Activity Interest (Scale: 0 to 10)
        # Culture, Adventure, Relaxation, Nightlife
        self.var_culture = self._create_activity_variable("culture")
        self.var_adventure = self._create_activity_variable("adventure")
        self.var_relaxation = self._create_activity_variable("relaxation")
        self.var_nightlife = self._create_activity_variable("nightlife")

        # 5. Output Variable: Suitability Score (0 to 100 %) [Universe: 0 to 100]
        self.var_suitability = LinguisticVariable("suitability", (0.0, 100.0), "%")
        self.var_suitability.add_trapezoidal("Poor", 0.0, 0.0, 20.0, 35.0)
        self.var_suitability.add_triangular("Moderate", 25.0, 50.0, 70.0)
        self.var_suitability.add_triangular("High", 60.0, 75.0, 90.0)
        self.var_suitability.add_trapezoidal("Excellent", 80.0, 90.0, 100.0, 100.0)

        # Initialize Expert Rule Base
        self.rules: List[FuzzyRule] = []
        self._build_expert_rule_base()

    def _create_activity_variable(self, name: str) -> LinguisticVariable:
        var = LinguisticVariable(name, (0.0, 10.0), "/10")
        var.add_trapezoidal("Low", 0.0, 0.0, 2.5, 4.5)
        var.add_triangular("Medium", 3.5, 5.5, 7.5)
        var.add_trapezoidal("High", 6.5, 8.5, 10.0, 10.0)
        return var

    def _build_expert_rule_base(self):
        """
        Builds a comprehensive expert rule base of 36 rules linking tourist preferences
        with all 6 archetypes. Covers High, Medium, and Low levels with Poor, Moderate, High, and Excellent consequents.
        """
        rule_defs = [
            # -------------------------------------------------------------
            # Category 1: Cultural & Heritage City (6 rules)
            # -------------------------------------------------------------
            ("R01", {"culture": "High", "duration": "Short", "climate": "Mild"},
             {"archetype": DestinationArchetype.CULTURAL_HERITAGE, "suitability": "Excellent"},
             "Σύντομο πολιτιστικό city break σε ήπιο καιρό"),

            ("R02", {"culture": "High", "budget": "Medium"},
             {"archetype": DestinationArchetype.CULTURAL_HERITAGE, "suitability": "High"},
             "Πολιτιστικός προορισμός με μεσαίο προϋπολογισμό"),

            ("R03", {"culture": "High", "budget": "High"},
             {"archetype": DestinationArchetype.CULTURAL_HERITAGE, "suitability": "Excellent"},
             "Πλούσιο πολιτιστικό ταξίδι με υψηλό προϋπολογισμό"),

            ("R04", {"culture": "Medium", "climate": "Mild"},
             {"archetype": DestinationArchetype.CULTURAL_HERITAGE, "suitability": "Moderate"},
             "Μέτριο πολιτιστικό ενδιαφέρον σε ευχάριστο ήπιο κλίμα"),

            ("R05", {"culture": "Medium", "duration": "Short"},
             {"archetype": DestinationArchetype.CULTURAL_HERITAGE, "suitability": "Moderate"},
             "Σύντομη απόδραση με ισορροπημένο ενδιαφέρον για μουσεία"),

            ("R06", {"culture": "Low"},
             {"archetype": DestinationArchetype.CULTURAL_HERITAGE, "suitability": "Poor"},
             "Χαμηλό ενδιαφέρον για ιστορία και μουσεία"),

            # -------------------------------------------------------------
            # Category 2: Coastal & Island Relaxation (6 rules)
            # -------------------------------------------------------------
            ("R07", {"relaxation": "High", "climate": "Warm", "duration": "Medium"},
             {"archetype": DestinationArchetype.ISLAND_RELAXATION, "suitability": "Excellent"},
             "Ιδανικές παραθαλάσσιες διακοπές χαλάρωσης σε ζεστό κλίμα"),

            ("R08", {"relaxation": "High", "climate": "Warm", "duration": "Long"},
             {"archetype": DestinationArchetype.ISLAND_RELAXATION, "suitability": "Excellent"},
             "Πολυήμερες θερινές διακοπές ανάπαυλας σε νησί"),

            ("R09", {"relaxation": "High", "climate": "Warm"},
             {"archetype": DestinationArchetype.ISLAND_RELAXATION, "suitability": "High"},
             "Έντονη επιθυμία χαλάρωσης σε θερμό περιβάλλον"),

            ("R10", {"relaxation": "Medium", "climate": "Warm"},
             {"archetype": DestinationArchetype.ISLAND_RELAXATION, "suitability": "Moderate"},
             "Μέτρια χαλάρωση σε θερμό καλοκαιρινό προορισμό"),

            ("R11", {"relaxation": "High", "climate": "Cold"},
             {"archetype": DestinationArchetype.ISLAND_RELAXATION, "suitability": "Poor"},
             "Παραθαλάσσια χαλάρωση ασύμβατη με ψυχρό κλίμα"),

            ("R12", {"relaxation": "Low"},
             {"archetype": DestinationArchetype.ISLAND_RELAXATION, "suitability": "Poor"},
             "Χαμηλή προτεραιότητα σε παραλίες και ανάπαυλα"),

            # -------------------------------------------------------------
            # Category 3: Alpine & Mountain Adventure (6 rules)
            # -------------------------------------------------------------
            ("R13", {"adventure": "High", "climate": "Cold"},
             {"archetype": DestinationArchetype.MOUNTAIN_ADVENTURE, "suitability": "Excellent"},
             "Ορεινή περιπέτεια και χειμερινά σπορ σε ψυχρό κλίμα"),

            ("R14", {"adventure": "High", "budget": "Low"},
             {"archetype": DestinationArchetype.MOUNTAIN_ADVENTURE, "suitability": "High"},
             "Backpacking και υπαίθρια περιπέτεια με χαμηλό κόστος"),

            ("R15", {"adventure": "High", "duration": "Medium", "climate": "Mild"},
             {"archetype": DestinationArchetype.MOUNTAIN_ADVENTURE, "suitability": "High"},
             "Πεζοπορία και δραστηριότητες βουνού σε εύκρατο κλίμα"),

            ("R16", {"adventure": "Medium", "climate": "Cold"},
             {"archetype": DestinationArchetype.MOUNTAIN_ADVENTURE, "suitability": "Moderate"},
             "Μέτρια ορεινή δραστηριότητα σε δροσερό κλίμα"),

            ("R17", {"adventure": "Medium", "climate": "Mild"},
             {"archetype": DestinationArchetype.MOUNTAIN_ADVENTURE, "suitability": "Moderate"},
             "Ήπια επαφή με τη φύση και πεζοπορία"),

            ("R18", {"adventure": "Low"},
             {"archetype": DestinationArchetype.MOUNTAIN_ADVENTURE, "suitability": "Poor"},
             "Χαμηλό ενδιαφέρον για περιπέτεια και ορειβασία"),

            # -------------------------------------------------------------
            # Category 4: Luxury & Premium Wellness (6 rules)
            # -------------------------------------------------------------
            ("R19", {"relaxation": "High", "budget": "High", "climate": "Warm"},
             {"archetype": DestinationArchetype.LUXURY_ESCORT, "suitability": "Excellent"},
             "Πολυτελής καλοκαιρινή χαλάρωση σε premium resort"),

            ("R20", {"budget": "High", "relaxation": "High"},
             {"archetype": DestinationArchetype.LUXURY_ESCORT, "suitability": "Excellent"},
             "Υψηλός προϋπολογισμός με προτεραιότητα στην πολυτέλεια"),

            ("R21", {"climate": "Cold", "relaxation": "High", "budget": "High"},
             {"archetype": DestinationArchetype.LUXURY_ESCORT, "suitability": "High"},
             "Χειμερινό luxury σαλέ και spa σε ορεινό τοπίο"),

            ("R22", {"budget": "Medium", "relaxation": "High"},
             {"archetype": DestinationArchetype.LUXURY_ESCORT, "suitability": "Moderate"},
             "Επιθυμία ευεξίας με μεσαίο διαθέσιμο προϋπολογισμό"),

            ("R23", {"budget": "Low", "duration": "Long"},
             {"archetype": DestinationArchetype.LUXURY_ESCORT, "suitability": "Poor"},
             "Περιορισμένος προϋπολογισμός για πολυήμερο πολυτελές ταξίδι"),

            ("R24", {"budget": "Low"},
             {"archetype": DestinationArchetype.LUXURY_ESCORT, "suitability": "Poor"},
             "Χαμηλός προϋπολογισμός ασύμβατος με premium διαμονή"),

            # -------------------------------------------------------------
            # Category 5: Vibrant Urban & Entertainment (6 rules)
            # -------------------------------------------------------------
            ("R25", {"nightlife": "High", "duration": "Short", "budget": "Low"},
             {"archetype": DestinationArchetype.VIBRANT_NIGHTLIFE, "suitability": "High"},
             "Νεανικό weekend διασκέδασης με χαμηλό κόστος"),

            ("R26", {"nightlife": "High", "budget": "Medium", "duration": "Short"},
             {"archetype": DestinationArchetype.VIBRANT_NIGHTLIFE, "suitability": "Excellent"},
             "Κοσμοπολίτικο city break με έντονη ψυχαγωγία"),

            ("R27", {"nightlife": "High", "budget": "High"},
             {"archetype": DestinationArchetype.VIBRANT_NIGHTLIFE, "suitability": "Excellent"},
             "Premium νυχτερινή ζωή και clubbing σε μητροπόλεις"),

            ("R28", {"nightlife": "Medium", "duration": "Short"},
             {"archetype": DestinationArchetype.VIBRANT_NIGHTLIFE, "suitability": "Moderate"},
             "Μέτρια διάθεση για έξοδο σε σύντομο ταξίδι πόλης"),

            ("R29", {"nightlife": "Medium", "culture": "High"},
             {"archetype": DestinationArchetype.VIBRANT_NIGHTLIFE, "suitability": "Moderate"},
             "Συνδυασμός πολιτιστικής ημέρας με βραδινή έξοδο"),

            ("R30", {"nightlife": "Low"},
             {"archetype": DestinationArchetype.VIBRANT_NIGHTLIFE, "suitability": "Poor"},
             "Χαμηλό ενδιαφέρον για νυχτερινή διασκέδαση και κλαμπ"),

            # -------------------------------------------------------------
            # Category 6: Exotic & Tropical Explorer (6 rules)
            # -------------------------------------------------------------
            ("R31", {"adventure": "High", "duration": "Long", "climate": "Warm"},
             {"archetype": DestinationArchetype.EXOTIC_EXPLORATION, "suitability": "Excellent"},
             "Εξωτική μακρινή εξερεύνηση σε θερμό προορισμό"),

            ("R32", {"culture": "High", "adventure": "High", "duration": "Long"},
             {"archetype": DestinationArchetype.EXOTIC_EXPLORATION, "suitability": "Excellent"},
             "Πολυήμερο ταξίδι ανακάλυψης πλούσιων εμπειριών"),

            ("R33", {"adventure": "High", "climate": "Warm"},
             {"archetype": DestinationArchetype.EXOTIC_EXPLORATION, "suitability": "High"},
             "Περιπέτεια σε τροπικό ή εξωτικό περιβάλλον"),

            ("R34", {"adventure": "Medium", "duration": "Long", "climate": "Warm"},
             {"archetype": DestinationArchetype.EXOTIC_EXPLORATION, "suitability": "Moderate"},
             "Πολυήμερο ταξίδι με μέτρια περιπέτεια σε ζεστό κλίμα"),

            ("R35", {"culture": "Medium", "adventure": "Medium", "duration": "Long"},
             {"archetype": DestinationArchetype.EXOTIC_EXPLORATION, "suitability": "Moderate"},
             "Ισορροπημένη εξερεύνηση μακρινού προορισμού"),

            ("R36", {"duration": "Short", "budget": "Low"},
             {"archetype": DestinationArchetype.EXOTIC_EXPLORATION, "suitability": "Poor"},
             "Σύντομος χρόνος και χαμηλό budget για μακρινό εξωτικό ταξίδι")
        ]

        for rid, ante, conseq, desc in rule_defs:
            self.rules.append(FuzzyRule(rid, ante, conseq, weight=1.0, description=desc))

    def fuzzify_inputs(self, user_inputs: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """
        Fuzzifies raw numerical inputs into linguistic term memberships.
        Input keys: 'budget', 'climate', 'duration', 'culture', 'adventure', 'relaxation', 'nightlife'.
        """
        fuzzified = {
            "budget": self.var_budget.fuzzify(user_inputs.get("budget", 1000.0)),
            "climate": self.var_climate.fuzzify(user_inputs.get("climate", 22.0)),
            "duration": self.var_duration.fuzzify(user_inputs.get("duration", 5.0)),
            "culture": self.var_culture.fuzzify(user_inputs.get("culture", 5.0)),
            "adventure": self.var_adventure.fuzzify(user_inputs.get("adventure", 5.0)),
            "relaxation": self.var_relaxation.fuzzify(user_inputs.get("relaxation", 5.0)),
            "nightlife": self.var_nightlife.fuzzify(user_inputs.get("nightlife", 5.0)),
        }
        return fuzzified

    def evaluate_rules(self, fuzzified: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """
        Evaluates fuzzy rules using Min operator for antecedents (AND).
        Returns active rules with their firing strengths (alpha cut / firing strength).
        """
        active_rules = []
        for rule in self.rules:
            terms_strengths = []
            for var_name, term_name in rule.antecedent.items():
                degree = fuzzified.get(var_name, {}).get(term_name, 0.0)
                terms_strengths.append(degree)

            # Mamdani AND inference: min of antecedent membership degrees
            firing_strength = min(terms_strengths) if terms_strengths else 0.0
            firing_strength *= rule.weight

            if firing_strength > 0.01:
                active_rules.append({
                    "rule_id": rule.rule_id,
                    "strength": round(firing_strength, 4),
                    "archetype": rule.consequent.get("archetype"),
                    "suitability_term": rule.consequent.get("suitability"),
                    "description": rule.description,
                    "antecedent": rule.antecedent
                })

        # Sort by firing strength descending
        active_rules.sort(key=lambda x: x["strength"], reverse=True)
        return active_rules

    def defuzzify_centroid(self, active_rules: List[Dict[str, Any]], archetype: str = None) -> float:
        """
        Performs Centroid Defuzzification (Center of Gravity - COG)
        z* = sum(z * mu(z)) / sum(mu(z))
        If archetype is provided, filters active rules affecting that archetype.
        When no rules fire for an archetype, returns a low baseline score of 10.0%
        (instead of neutral 50.0%) so that unactivated archetypes do not rank above
        archetypes that actively fired a 'Poor' rule.
        """
        z_universe = np.linspace(0.0, 100.0, 201)
        aggregated_membership = np.zeros_like(z_universe)

        filtered_rules = active_rules
        if archetype is not None:
            filtered_rules = [r for r in active_rules if r["archetype"] == archetype]

        if not filtered_rules:
            # Χαμηλό ουδέτερο σκορ (10.0%) όταν δεν ενεργοποιείται κανένας κανόνας για τον αρχέτυπο
            return 10.0

        # Aggregate clipped output membership functions (Mamdani Max-Min)
        for r in filtered_rules:
            term = r["suitability_term"]
            strength = r["strength"]
            fset = self.var_suitability.sets.get(term)
            if fset:
                term_vals = fset.membership(z_universe)
                clipped = np.minimum(term_vals, strength)
                aggregated_membership = np.maximum(aggregated_membership, clipped)

        sum_mu = np.sum(aggregated_membership)
        if sum_mu == 0:
            return 10.0

        cog = float(np.sum(z_universe * aggregated_membership) / sum_mu)
        return round(cog, 2)

    def compute_archetype_affinities(self, active_rules: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Computes defuzzified suitability score (0-100%) for each destination archetype.
        """
        all_archetypes = [
            DestinationArchetype.CULTURAL_HERITAGE,
            DestinationArchetype.ISLAND_RELAXATION,
            DestinationArchetype.MOUNTAIN_ADVENTURE,
            DestinationArchetype.LUXURY_ESCORT,
            DestinationArchetype.VIBRANT_NIGHTLIFE,
            DestinationArchetype.EXOTIC_EXPLORATION
        ]

        affinities = {}
        for arch in all_archetypes:
            score = self.defuzzify_centroid(active_rules, archetype=arch)
            affinities[arch] = score

        return affinities
