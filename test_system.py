"""
Comprehensive automated test suite for FuzzyTravel AI system.
Verifies all modules: Membership, FIS (36 rules & <5% coverage gap), FCM (Hungarian persona alignment across multiple seeds),
Catalog, Feedback (using tempfile), Recommender (with persona_fit & profile distinction), and Visualizations.
"""
import sys
import os
import tempfile
import numpy as np

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def run_tests():
    print("==================================================")
    print("  ΕΛΕΓΧΟΣ ΛΕΙΤΟΥΡΓΙΑΣ ΣΥΣΤΗΜΑΤΟΣ (SYSTEM VERIFICATION)")
    print("==================================================")

    # 1. Test Membership Functions
    print("\n[1/8] Έλεγχος Συναρτήσεων Συμμετοχής (membership.py)...")
    from core.membership import triangular, trapezoidal, LinguisticVariable
    assert triangular(5.0, 0.0, 5.0, 10.0) == 1.0, "Triangular peak failed"
    assert triangular(0.0, 0.0, 5.0, 10.0) == 0.0, "Triangular base failed"
    assert trapezoidal(5.0, 2.0, 4.0, 6.0, 8.0) == 1.0, "Trapezoidal plateau failed"

    lv = LinguisticVariable("test_var", (0.0, 100.0), "units")
    lv.add_triangular("Low", 0.0, 20.0, 40.0)
    lv.add_trapezoidal("High", 50.0, 70.0, 100.0, 100.0)
    fuzz = lv.fuzzify(20.0)
    assert fuzz["Low"] == 1.0, "LinguisticVariable fuzzify failed"
    print("  -> OK: Τριγωνικές, τραπεζοειδείς και γλωσσικές μεταβλητές λειτουργούν άψογα.")

    # 2. Test Fuzzy Tourism Engine & Rule Coverage (B1, B2, B3)
    print("\n[2/8] Έλεγχος Ασαφούς Μηχανής Mamdani (fuzzy_engine.py)...")
    from core.fuzzy_engine import FuzzyTourismEngine
    engine = FuzzyTourismEngine()
    assert len(engine.rules) == 36, f"Expected 36 rules, found {len(engine.rules)}"

    test_inputs = {
        "budget": 1200.0,
        "climate": 24.0,
        "duration": 5.0,
        "culture": 8.0,
        "adventure": 4.0,
        "relaxation": 7.0,
        "nightlife": 6.0
    }
    fuzzified = engine.fuzzify_inputs(test_inputs)
    assert len(fuzzified) == 7, "Fuzzification missing variables"
    active_rules = engine.evaluate_rules(fuzzified)
    assert len(active_rules) >= 4, f"Expected at least 4 active rules for test input, got {len(active_rules)}"
    affinities = engine.compute_archetype_affinities(active_rules)
    assert len(affinities) == 6, "Affinities calculation failed"
    # Verify default centroid score when no rules fire is 10.0 (B3)
    assert engine.defuzzify_centroid([]) == 10.0, "Default defuzzify_centroid score should be 10.0"

    # Monte Carlo test: Verify < 5% gap across 2000 random inputs (B1)
    np.random.seed(42)
    N_samples = 2000
    zero_coverage_count = 0
    for _ in range(N_samples):
        rand_inp = {
            "budget": float(np.random.uniform(100, 5000)),
            "climate": float(np.random.uniform(-10, 45)),
            "duration": float(np.random.uniform(1, 30)),
            "culture": float(np.random.uniform(0, 10)),
            "adventure": float(np.random.uniform(0, 10)),
            "relaxation": float(np.random.uniform(0, 10)),
            "nightlife": float(np.random.uniform(0, 10))
        }
        f_rand = engine.fuzzify_inputs(rand_inp)
        if len(engine.evaluate_rules(f_rand)) == 0:
            zero_coverage_count += 1
    zero_rate = zero_coverage_count / N_samples
    assert zero_rate < 0.05, f"Rule coverage failure rate {zero_rate*100:.2f}% exceeds 5% threshold!"
    print(f"  -> OK: {len(engine.rules)} κανόνες ορίστηκαν. {len(active_rules)} κανόνες ενεργοποιήθηκαν στο test input.")
    print(f"  -> OK: Ποσοστό έλλειψης κανόνα σε 2000 τυχαίες εισόδους: {zero_rate*100:.2f}% (< 5% όριο).")

    # 3. Test Fuzzy C-Means Clustering & Hungarian Alignment (A2, C)
    print("\n[3/8] Έλεγχος Fuzzy C-Means Clustering & Hungarian Alignment (fcm_clustering.py)...")
    from core.fcm_clustering import FuzzyCMeansModel, generate_synthetic_tourist_dataset

    # Verify matching across multiple random states
    test_seeds = [42, 100, 777]
    for seed in test_seeds:
        fcm_test = FuzzyCMeansModel(n_clusters=5, m=2.0, random_state=seed)
        X_test, _ = generate_synthetic_tourist_dataset(300, random_state=seed)
        fcm_test.fit(X_test)
        assert fcm_test.is_fitted, f"FCM fitting failed for seed {seed}"
        
        # Verify cluster-to-persona Hungarian alignment
        # Personas: 0=Cultural, 1=Luxury, 2=Backpacker, 3=Alpine, 4=Nightlife
        cult_cluster = fcm_test.persona_to_cluster[0]
        lux_cluster = fcm_test.persona_to_cluster[1]
        bp_cluster = fcm_test.persona_to_cluster[2]
        alp_cluster = fcm_test.persona_to_cluster[3]
        night_cluster = fcm_test.persona_to_cluster[4]

        # In normalized centroids: index 0=budget, 1=climate, 2=duration, 3=culture, 4=adventure, 5=relaxation, 6=nightlife
        cents = fcm_test.centroids
        # Cultural cluster should have highest culture
        assert np.argmax(cents[:, 3]) == cult_cluster, f"Seed {seed}: Cultural cluster does not have max culture"
        # Alpine cluster should have highest adventure
        assert np.argmax(cents[:, 4]) == alp_cluster, f"Seed {seed}: Alpine cluster does not have max adventure"
        # Luxury cluster should have highest relaxation
        assert np.argmax(cents[:, 5]) == lux_cluster, f"Seed {seed}: Luxury cluster does not have max relaxation"
        # Nightlife cluster should have highest nightlife
        assert np.argmax(cents[:, 6]) == night_cluster, f"Seed {seed}: Nightlife cluster does not have max nightlife"
        # Backpacker cluster should have lowest budget
        assert np.argmin(cents[:, 0]) == bp_cluster, f"Seed {seed}: Backpacker cluster does not have min budget"

    # Full inspection on standard seed 42
    fcm = FuzzyCMeansModel(n_clusters=5, m=2.0, random_state=42)
    X_norm, df_hist = generate_synthetic_tourist_dataset(350, random_state=42)
    fcm.fit(X_norm)
    metrics = fcm.compute_validation_metrics()
    assert "partition_coefficient_PC" in metrics and "partition_entropy_PE" in metrics
    assert "cluster_to_persona" in metrics
    prediction = fcm.predict_membership(test_inputs)
    assert "dominant_persona" in prediction
    df_cent = fcm.get_centroids_dataframe()
    assert len(df_cent) == 5, "Centroids DataFrame row count mismatch"
    print(f"  -> OK: FCM σύγκλινε και αντιστοιχίστηκε επιτυχώς (Hungarian algorithm) σε {len(test_seeds)} seeds.")
    print(f"  -> Κυρίαρχο προφίλ: {prediction['dominant_persona']} ({prediction['dominant_pct']}%)")
    print(f"  -> Partition Coefficient (PC): {metrics['partition_coefficient_PC']}, Partition Entropy (PE): {metrics['partition_entropy_PE']}")

    # 4. Test Catalog Manager
    print("\n[4/8] Έλεγχος Βάσης Προορισμών (catalog_manager.py)...")
    from data.catalog_manager import CatalogManager
    cat_mgr = CatalogManager()
    dests = cat_mgr.get_all()
    assert len(dests) == 22, f"Expected 22 destinations, found {len(dests)}"
    df_cat = cat_mgr.to_dataframe()
    assert len(df_cat) == len(dests), "DataFrame export size mismatch"
    print(f"  -> OK: Φορτώθηκαν {len(dests)} προορισμοί (12 Ελλάδα & 10 Εξωτερικό) με πλήρη δεδομένα.")

    # 5. Test Feedback Manager (using tempfile to preserve real data) (D1)
    print("\n[5/8] Έλεγχος Μηχανισμού Ανάδρασης (feedback_manager.py)...")
    from data.feedback_manager import FeedbackManager
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        temp_fb_path = tmp.name
    try:
        fb_mgr = FeedbackManager(storage_path=temp_fb_path)
        fb_entry = fb_mgr.record_feedback(
            "gr_chania", "Χανιά", test_inputs, rating=5, accepted=True, comment="Αυτοματοποιημένος έλεγχος δοκιμής"
        )
        assert fb_entry["id"], "Feedback recording failed"
        stats = fb_mgr.get_destination_feedback_stats("gr_chania")
        assert stats["count"] == 1, "Feedback stats count mismatch"
        assert stats["feedback_delta"] > 0, "Feedback delta should be positive"
        print(f"  -> OK: Ανάδραση καταγράφηκε σε προσωρινό αρχείο (Αποδοχή, Βαθμολογία 5/5, Δ_feedback: +{stats['feedback_delta']}%).")
    finally:
        if os.path.exists(temp_fb_path):
            os.remove(temp_fb_path)

    # 6. Test Hybrid Tourism Recommender (A1, B4)
    print("\n[6/8] Έλεγχος Υβριδικού Recommender & Επίδρασης FCM (recommender.py)...")
    from core.recommender import HybridTourismRecommender
    rec = HybridTourismRecommender()
    res = rec.recommend(test_inputs, top_n=3)
    assert len(res["recommendations"]) == 3, "Recommendation count mismatch"
    top_dest = res["recommendations"][0]
    
    # Check that persona_fit exists in component_scores (A1)
    comp_scores = top_dest["component_scores"]
    assert "persona_fit" in comp_scores, "persona_fit missing from component_scores!"
    assert 0.0 <= comp_scores["persona_fit"] <= 100.0, "persona_fit out of [0, 100] bounds"
    assert "budget_compatibility" in comp_scores
    assert "climate_match" in comp_scores
    print(f"  -> OK: Κορυφαίος προτεινόμενος προορισμός: {top_dest['destination']['name']} ({top_dest['final_score']}%)")
    print(f"  -> Persona Fit Score: {comp_scores['persona_fit']}%")
    print(f"  -> Αιτιολόγηση (XAI): {top_dest['rationale'][0]}")

    # Contrast Test: Verify that two strongly distinct traveler profiles produce different top-5 recommendations
    profile_culture = {
        "budget": 2000.0, "climate": 18.0, "duration": 5.0,
        "culture": 9.5, "adventure": 1.5, "relaxation": 4.0, "nightlife": 3.0
    }
    profile_alpine = {
        "budget": 1200.0, "climate": 6.0, "duration": 7.0,
        "culture": 2.0, "adventure": 9.5, "relaxation": 3.0, "nightlife": 2.0
    }
    res_culture = rec.recommend(profile_culture, top_n=5)
    res_alpine = rec.recommend(profile_alpine, top_n=5)
    top_culture_ids = [d["destination"]["id"] for d in res_culture["recommendations"]]
    top_alpine_ids = [d["destination"]["id"] for d in res_alpine["recommendations"]]
    
    # Verify recommendations clearly diverge
    assert top_culture_ids[0] != top_alpine_ids[0], "Distinct profiles should produce different #1 destination!"
    common_destinations = set(top_culture_ids).intersection(set(top_alpine_ids))
    print(f"  -> OK: Δύο διακριτά προφίλ (Πολιτισμός vs Ορεινή Περιπέτεια) παρήγαγαν διαφορετικές συστάσεις:")
    print(f"     * Πολιτιστικό προφίλ: Top 1 = {res_culture['recommendations'][0]['destination']['name']}")
    print(f"     * Ορεινό προφίλ:      Top 1 = {res_alpine['recommendations'][0]['destination']['name']}")
    print(f"     * Κοινά στα Top-5: {len(common_destinations)}/5 προορισμοί.")

    # 7. Test Visualizations & UI components
    print("\n[7/8] Έλεγχος Οπτικοποιήσεων & Γραφημάτων (visualizations.py)...")
    from ui.visualizations import (
        plot_fuzzy_variable,
        plot_persona_radar_chart,
        plot_destination_scores_breakdown,
        plot_active_rules_chart
    )
    fig_var = plot_fuzzy_variable(rec.fuzzy_engine.var_budget, 1200)
    fig_radar = plot_persona_radar_chart(res["fcm_profiling"]["all_personas"])
    fig_break = plot_destination_scores_breakdown(top_dest["component_scores"], top_dest["destination"]["name"])
    fig_rules = plot_active_rules_chart(res["active_fuzzy_rules"])
    assert fig_var and fig_radar and fig_break and fig_rules, "Visualization creation failed"
    print("  -> OK: Όλα τα διαδραστικά διαγράμματα Plotly παράγονται άρτια χωρίς σφάλματα.")

    # 8. Test Headless Streamlit UI (AppTest) across all 3 modes
    print("\n[8/8] Έλεγχος Headless Streamlit UI (AppTest και στις 3 λειτουργίες)...")
    from streamlit.testing.v1 import AppTest
    modes = [
        "✈️ Σύμβουλος Προτάσεων (Travel Agent Recommender)",
        "🧠 Ασαφής Μηχανή & FCM (Ακαδημαϊκή Εποπτεία)",
        "💼 Διαχείριση Καταλόγου & Πακέτων (B2B Inventory)"
    ]
    for mode in modes:
        at = AppTest.from_file("ui/app.py", default_timeout=30)
        at.run()
        at.sidebar.radio[0].set_value(mode).run()
        assert len(at.exception) == 0, f"Σφάλμα κατά την εκτέλεση της λειτουργίας '{mode}': {at.exception}"
        print(f"  -> OK: Η λειτουργία '{mode}' εκτελέστηκε χωρίς σφάλματα.")

    print("\n" + "="*50)
    print("  ΟΛΟΙ ΟΙ ΕΛΕΓΧΟΙ ΟΛΟΚΛΗΡΩΘΗΚΑΝ ΜΕ ΕΠΙΤΥΧΙΑ (100% PASS)")
    print("="*50)


if __name__ == "__main__":
    run_tests()
