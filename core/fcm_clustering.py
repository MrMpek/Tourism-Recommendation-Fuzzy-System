"""
Fuzzy C-Means (FCM) Clustering Module.
Implements Bezdek's algorithm for soft clustering of tourists into behavioral personas.
Includes mathematical objective calculation, cluster validation metrics (PC, PE),
optimal persona matching via Hungarian algorithm (linear_sum_assignment),
and inference for new incoming user queries.
"""
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


class TouristPersona:
    """Represents a discovered tourist persona archetype."""
    def __init__(
        self,
        persona_id: int,
        name: str,
        greek_name: str,
        description: str,
        key_traits: List[str],
        prototype_raw: Dict[str, float]
    ):
        self.persona_id = persona_id
        self.name = name
        self.greek_name = greek_name
        self.description = description
        self.key_traits = key_traits
        self.prototype_raw = prototype_raw


class FuzzyCMeansModel:
    """
    Mathematical implementation of Fuzzy C-Means (FCM) algorithm.
    Optimizes Bezdek's objective function:
        J_m = sum_{i=1}^N sum_{j=1}^C (u_ij)^m * ||x_i - v_j||^2
    """
    FEATURE_NAMES = [
        "budget_norm",
        "climate_norm",
        "duration_norm",
        "culture_norm",
        "adventure_norm",
        "relaxation_norm",
        "nightlife_norm"
    ]

    PERSONA_DEFINITIONS = [
        TouristPersona(
            0,
            "Cultural & Heritage Explorer",
            "Εξερευνητής Πολιτισμού & Ιστορίας",
            "Ταξιδιώτης με έντονο ενδιαφέρον για μουσεία, αρχαιολογικούς χώρους, αρχιτεκτονική και τοπική γαστρονομία σε εύκρατο κλίμα.",
            ["Υψηλή πολιτιστική συνάφεια", "Ήπιο κλίμα", "Ευρωπαϊκές πρωτεύουσες & ιστορικές πόλεις"],
            {"budget": 1800.0, "climate": 19.0, "duration": 6.0, "culture": 8.65, "adventure": 3.5, "relaxation": 5.5, "nightlife": 4.5}
        ),
        TouristPersona(
            1,
            "Luxury & Wellness Relaxer",
            "Ταξιδιώτης Πολυτέλειας & Ευεξίας",
            "Αποζητά άνεση, premium ξενοδοχεία 5 αστέρων, spa, γαστρονομία υψηλής ραπτικής και απόλυτη χαλάρωση σε ζεστούς προορισμούς.",
            ["Υψηλός προϋπολογισμός", "Χαλάρωση & Resort", "Θερμό/νησιωτικό κλίμα"],
            {"budget": 3800.0, "climate": 30.0, "duration": 9.0, "culture": 4.5, "adventure": 2.5, "relaxation": 9.25, "nightlife": 5.75}
        ),
        TouristPersona(
            2,
            "Budget Backpacker & Youth Nomad",
            "Οικονομικός Backpacker & Νεανικός Εξερευνητής",
            "Νέος ή low-budget ταξιδιώτης που αναζητά αυθεντικές εμπειρίες, hostels, κοινωνικοποίηση και εξοικονόμηση πόρων.",
            ["Χαμηλό κόστος", "Ευελιξία", "Αυθεντικότητα & Social vibe"],
            {"budget": 425.0, "climate": 24.0, "duration": 4.5, "culture": 5.5, "adventure": 8.0, "relaxation": 3.5, "nightlife": 7.75}
        ),
        TouristPersona(
            3,
            "Alpine & Nature Adventure Seeker",
            "Λάτρης Φύσης & Ορεινής Περιπέτειας",
            "Ενθουσιώδης με trekking, ορειβασία, extreme sports, φαράγγια και φυσικά τοπία σε ορεινό ή δροσερό περιβάλλον.",
            ["Υψηλή περιπέτεια", "Επαφή με τη φύση", "Δροσερό/ψυχρό κλίμα"],
            {"budget": 1300.0, "climate": 9.0, "duration": 7.5, "culture": 3.5, "adventure": 9.25, "relaxation": 4.5, "nightlife": 2.5}
        ),
        TouristPersona(
            4,
            "Cosmopolitan & Nightlife Vibe",
            "Κοσμοπολίτης της Νυχτερινής Ζωής",
            "Εστιάζει σε ζωντανές μητροπόλεις, bar hopping, μουσικά festivals, clubbing, γρήγορους ρυθμούς και σύντομες αποδράσεις.",
            ["Έντονη νυχτερινή ζωή", "City breaks", "Ψυχαγωγία & Διασκέδαση"],
            {"budget": 1150.0, "climate": 23.0, "duration": 3.0, "culture": 5.5, "adventure": 3.5, "relaxation": 3.5, "nightlife": 9.25}
        )
    ]

    def __init__(self, n_clusters: int = 5, m: float = 2.0, max_iter: int = 150, tol: float = 1e-5, random_state: int = 42):
        self.n_clusters = n_clusters
        self.m = m  # Fuzzifier parameter (standard m=2)
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state

        self.centroids: Optional[np.ndarray] = None  # Shape: (C, D)
        self.u_matrix: Optional[np.ndarray] = None   # Shape: (N, C)
        self.cost_history: List[float] = []
        self.is_fitted = False

        # Cluster to persona mappings (resolved via Hungarian algorithm)
        self.cluster_to_persona: Dict[int, int] = {}
        self.persona_to_cluster: Dict[int, int] = {}

        # Min-Max normalization bounds
        self.bounds = {
            "budget": (100.0, 5000.0),
            "climate": (-10.0, 45.0),
            "duration": (1.0, 30.0),
            "culture": (0.0, 10.0),
            "adventure": (0.0, 10.0),
            "relaxation": (0.0, 10.0),
            "nightlife": (0.0, 10.0)
        }

    def normalize_vector(self, raw_dict: Dict[str, float]) -> np.ndarray:
        """Normalizes raw user preferences into [0, 1] range across the 7 feature dimensions."""
        vec = []
        for feat in ["budget", "climate", "duration", "culture", "adventure", "relaxation", "nightlife"]:
            val = float(raw_dict.get(feat, 5.0))
            low, high = self.bounds[feat]
            clamped = max(low, min(high, val))
            norm_val = (clamped - low) / (high - low)
            vec.append(norm_val)
        return np.array(vec, dtype=float)

    def denormalize_vector(self, norm_vec: np.ndarray) -> Dict[str, float]:
        """Denormalizes a [0, 1] vector back into real physical units (€, °C, days, /10)."""
        res = {}
        feats = ["budget", "climate", "duration", "culture", "adventure", "relaxation", "nightlife"]
        for idx, feat in enumerate(feats):
            low, high = self.bounds[feat]
            real_val = float(norm_vec[idx] * (high - low) + low)
            res[feat] = round(real_val, 2)
        return res

    def fit(self, X: np.ndarray) -> "FuzzyCMeansModel":
        """
        Fits Fuzzy C-Means on dataset X of shape (N, D).
        Uses alternating optimization between Centroids and Membership matrix,
        and subsequently aligns cluster centroids to predefined personas via Hungarian algorithm.
        """
        np.random.seed(self.random_state)
        n_samples, n_features = X.shape

        # Initialize membership matrix randomly and normalize rows to sum to 1
        U = np.random.uniform(0.01, 1.0, size=(n_samples, self.n_clusters))
        U = U / np.sum(U, axis=1, keepdims=True)

        self.cost_history = []

        for iteration in range(self.max_iter):
            # Step 1: Update centroids
            um = U ** self.m
            centroids = (um.T @ X) / np.sum(um.T, axis=1, keepdims=True)

            # Step 2: Compute Euclidean distances: d_ij = ||x_i - v_j||
            dists = np.zeros((n_samples, self.n_clusters))
            for j in range(self.n_clusters):
                dists[:, j] = np.linalg.norm(X - centroids[j], axis=1)

            # Avoid division by zero
            dists = np.fmax(dists, 1e-10)

            # Step 3: Compute Bezdek objective function
            cost = np.sum((U ** self.m) * (dists ** 2))
            self.cost_history.append(float(cost))

            # Step 4: Update membership matrix U
            power = 2.0 / (self.m - 1.0)
            inv_dists = dists ** (-power)
            U_new = inv_dists / np.sum(inv_dists, axis=1, keepdims=True)

            # Check convergence
            diff = np.linalg.norm(U_new - U)
            U = U_new

            if diff < self.tol:
                break

        self.centroids = centroids
        self.u_matrix = U

        # Step 5: Bipartite Matching (Hungarian algorithm) between centroids and persona prototypes
        # Ensures cluster identity matches domain definitions regardless of random initialization
        prototype_vectors = np.array([
            self.normalize_vector(p.prototype_raw) for p in self.PERSONA_DEFINITIONS
        ])  # Shape: (5, 7)

        cost_matrix = np.zeros((self.n_clusters, len(self.PERSONA_DEFINITIONS)))
        for c in range(self.n_clusters):
            for p in range(len(self.PERSONA_DEFINITIONS)):
                cost_matrix[c, p] = np.linalg.norm(self.centroids[c] - prototype_vectors[p])

        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        self.cluster_to_persona = {int(c): int(p) for c, p in zip(row_ind, col_ind)}
        self.persona_to_cluster = {int(p): int(c) for c, p in zip(row_ind, col_ind)}

        self.is_fitted = True
        return self

    def predict_membership(self, raw_input: Dict[str, float]) -> Dict[str, Any]:
        """
        Computes soft membership degrees u_j for an incoming traveler across all personas.
        Returns persona weights aligned to correct cluster personas.
        """
        if not self.is_fitted or self.centroids is None:
            raise ValueError("FCM model is not fitted yet.")

        x_norm = self.normalize_vector(raw_input)  # Shape (D,)

        # Distances to each centroid
        dists = np.linalg.norm(self.centroids - x_norm, axis=1)
        dists = np.fmax(dists, 1e-10)

        # Fuzzy membership formula: u_c = 1 / sum_{k=1}^C (d_c / d_k)^(2/(m-1))
        power = 2.0 / (self.m - 1.0)
        inv_dists = dists ** (-power)
        memberships = inv_dists / np.sum(inv_dists)

        persona_results = []
        for cluster_idx in range(self.n_clusters):
            p_idx = self.cluster_to_persona.get(cluster_idx, cluster_idx)
            persona = self.PERSONA_DEFINITIONS[p_idx]
            weight = float(memberships[cluster_idx])
            persona_results.append({
                "cluster_id": int(cluster_idx),
                "persona_id": int(p_idx),
                "name": persona.name,
                "greek_name": persona.greek_name,
                "description": persona.description,
                "traits": persona.key_traits,
                "membership_degree": round(weight, 4),
                "membership_pct": round(weight * 100.0, 1)
            })

        # Sort by membership degree descending
        persona_results.sort(key=lambda p: p["membership_degree"], reverse=True)
        dominant = persona_results[0]

        return {
            "dominant_persona": dominant["greek_name"],
            "dominant_pct": dominant["membership_pct"],
            "all_personas": persona_results,
            "raw_normalized_vector": x_norm.tolist()
        }

    def compute_validation_metrics(self) -> Dict[str, Any]:
        """
        Calculates Fuzzy Partition Coefficient (PC) and Partition Entropy (PE)
        - PC = (1/N) * sum_{i,j} (u_ij)^2   [ranges from 1/C to 1, higher is better]
        - PE = - (1/N) * sum_{i,j} u_ij * log(u_ij)  [ranges from 0 to log(C), lower is better]
        Also returns cluster-to-persona assignments.
        """
        if not self.is_fitted or self.u_matrix is None:
            return {}

        N = self.u_matrix.shape[0]
        pc = float(np.sum(self.u_matrix ** 2) / N)

        # Partition entropy
        u_safe = np.clip(self.u_matrix, 1e-12, 1.0)
        pe = float(-np.sum(u_safe * np.log(u_safe)) / N)

        assignments = {}
        for c, p in self.cluster_to_persona.items():
            assignments[f"Cluster_{c}"] = self.PERSONA_DEFINITIONS[p].name

        return {
            "partition_coefficient_PC": round(pc, 4),
            "partition_entropy_PE": round(pe, 4),
            "clusters_count": self.n_clusters,
            "iterations_to_converge": len(self.cost_history),
            "cluster_to_persona": self.cluster_to_persona,
            "persona_assignments": assignments
        }

    def get_centroids_dataframe(self) -> pd.DataFrame:
        """
        Returns a DataFrame of cluster centroids converted back to physical units
        (€, °C, days, /10), labeled with each cluster's aligned persona name.
        """
        if not self.is_fitted or self.centroids is None:
            return pd.DataFrame()

        rows = []
        for cluster_idx in range(self.n_clusters):
            p_idx = self.cluster_to_persona.get(cluster_idx, cluster_idx)
            persona = self.PERSONA_DEFINITIONS[p_idx]
            raw_vals = self.denormalize_vector(self.centroids[cluster_idx])
            rows.append({
                "Cluster ID": f"Cluster {cluster_idx}",
                "Persona": persona.greek_name,
                "English Name": persona.name,
                "Budget (€)": f"{int(raw_vals['budget'])} €",
                "Κλίμα (°C)": f"{raw_vals['climate']:.1f} °C",
                "Διάρκεια": f"{raw_vals['duration']:.1f} ημ.",
                "Πολιτισμός": f"{raw_vals['culture']:.1f}/10",
                "Περιπέτεια": f"{raw_vals['adventure']:.1f}/10",
                "Χαλάρωση": f"{raw_vals['relaxation']:.1f}/10",
                "Νυχτερινή Ζωή": f"{raw_vals['nightlife']:.1f}/10",
            })
        return pd.DataFrame(rows)


def generate_synthetic_tourist_dataset(n_samples: int = 350, random_state: int = 42) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    [Συνθετικό Σύνολο Δεδομένων (Synthetic Behavioral Dataset)]
    Generates a realistic synthetic historical dataset of 350 travelers representing
    diverse tourist personas in Greece and internationally.
    This synthetic dataset is explicitly designed for the academic evaluation and training
    of the Fuzzy C-Means (FCM) clustering model, modeling representative traveler behavioral patterns.
    """
    np.random.seed(random_state)
    records = []

    # Archetype centers in raw units
    archetypes = [
        # 0: Cultural Explorer: medium-high budget, mild climate, 4-8 days, high culture
        {"budget": (1200, 2400), "climate": (15, 23), "duration": (4, 8), "culture": (7.5, 9.8), "adventure": (2.0, 5.0), "relaxation": (4.0, 7.0), "nightlife": (3.0, 6.0)},
        # 1: Luxury & Wellness: high budget, warm climate, 6-12 days, high relaxation
        {"budget": (2800, 4800), "climate": (26, 34), "duration": (6, 12), "culture": (3.0, 6.0), "adventure": (1.0, 4.0), "relaxation": (8.5, 10.0), "nightlife": (4.0, 7.5)},
        # 2: Budget Backpacker: low budget, any climate, 3-6 days, high adventure/nightlife
        {"budget": (200, 650), "climate": (18, 30), "duration": (3, 6), "culture": (4.0, 7.0), "adventure": (6.5, 9.5), "relaxation": (2.0, 5.0), "nightlife": (6.0, 9.5)},
        # 3: Nature & Alpine: moderate budget, cold/mild climate, 5-10 days, high adventure
        {"budget": (800, 1800), "climate": (2, 16), "duration": (5, 10), "culture": (2.0, 5.0), "adventure": (8.5, 10.0), "relaxation": (3.0, 6.0), "nightlife": (1.0, 4.0)},
        # 4: Cosmopolitan Nightlife: medium budget, mild/warm, 2-4 days, high nightlife
        {"budget": (700, 1600), "climate": (18, 28), "duration": (2, 4), "culture": (4.0, 7.0), "adventure": (2.0, 5.0), "relaxation": (2.0, 5.0), "nightlife": (8.5, 10.0)},
    ]

    samples_per_arch = n_samples // len(archetypes)
    fcm_helper = FuzzyCMeansModel()

    for arch_id, bounds in enumerate(archetypes):
        for _ in range(samples_per_arch):
            entry = {
                "budget": np.random.uniform(bounds["budget"][0], bounds["budget"][1]),
                "climate": np.random.uniform(bounds["climate"][0], bounds["climate"][1]),
                "duration": np.random.uniform(bounds["duration"][0], bounds["duration"][1]),
                "culture": np.random.uniform(bounds["culture"][0], bounds["culture"][1]),
                "adventure": np.random.uniform(bounds["adventure"][0], bounds["adventure"][1]),
                "relaxation": np.random.uniform(bounds["relaxation"][0], bounds["relaxation"][1]),
                "nightlife": np.random.uniform(bounds["nightlife"][0], bounds["nightlife"][1]),
                "ground_truth_persona": FuzzyCMeansModel.PERSONA_DEFINITIONS[arch_id].name
            }
            records.append(entry)

    df = pd.DataFrame(records)

    # Create normalized X matrix
    X_norm = []
    for _, row in df.iterrows():
        vec = fcm_helper.normalize_vector(row.to_dict())
        X_norm.append(vec)
    X_norm = np.array(X_norm)

    return X_norm, df
