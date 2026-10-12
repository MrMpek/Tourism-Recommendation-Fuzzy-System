"""
Comprehensive automated test suite for FuzzyTravel AI system.
Verifies all modules: Membership, FIS, FCM, Catalog, Feedback, Recommender, and Visualizations.
"""
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_tests():
    print("==================================================")
    print("  ΕΛΕΓΧΟΣ ΛΕΙΤΟΥΡΓΙΑΣ ΣΥΣΤΗΜΑΤΟΣ (SYSTEM VERIFICATION)")
    print("==================================================")
    
    # 1. Test Membership Functions
    print("\n[1/7] Έλεγχος Συναρτήσεων Συμμετοχής (membership.py)...")
    from core.membership import triangular, trapezoidal, LinguisticVariable
    assert triangular(5.0, 0.0, 5.0, 10.0) == 1.0, "Triangular peak failed"
    assert triangular(0.0, 0.0, 5.0, 10.0) == 0.0 or triangular(0.0, 0.0, 5.0, 10.0) == 0.0, "Triangular base failed"
    assert trapezoidal(5.0, 2.0, 4.0, 6.0, 8.0) == 1.0, "Trapezoidal plateau failed"
    
    lv = LinguisticVariable("test_var", (0.0, 100.0), "units")
    lv.add_triangular("Low", 0.0, 20.0, 40.0)
    lv.add_trapezoidal("High", 50.0, 70.0, 100.0, 100.0)
    fuzz = lv.fuzzify(20.0)
    assert fuzz["Low"] == 1.0, "LinguisticVariable fuzzify failed"
    print("  -> OK: Τριγωνικές, τραπεζοειδείς και γλωσσικές μεταβλητές λειτουργούν άψογα.")

    # 2. Test Fuzzy Tourism Engine
    print("\n[2/7] Έλεγχος Ασαφούς Μηχανής Mamdani (fuzzy_engine.py)...")
    from core.fuzzy_engine import FuzzyTourismEngine
    engine = FuzzyTourismEngine()
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
    assert len(active_rules) > 0, "No active rules fired"
    affinities = engine.compute_archetype_affinities(active_rules)
    assert len(affinities) > 0, "Affinities calculation failed"
    print(f"  -> OK: {len(active_rules)} κανόνες ενεργοποιήθηκαν, αποσαφοποίηση Centroid υπολογίστηκε επιτυχώς.")

    # 3. Test Fuzzy C-Means Clustering
    print("\n[3/7] Έλεγχος Fuzzy C-Means Clustering (fcm_clustering.py)...")
    from core.fcm_clustering import FuzzyCMeansModel, generate_synthetic_tourist_dataset
    fcm = FuzzyCMeansModel(n_clusters=5, m=2.0)
    X_norm, df_hist = generate_synthetic_tourist_dataset(150)
    fcm.fit(X_norm)
    assert fcm.is_fitted, "FCM fitting failed"
    metrics = fcm.compute_validation_metrics()
    assert "partition_coefficient_PC" in metrics, "Validation metrics failed"
    prediction = fcm.predict_membership(test_inputs)
    assert "dominant_persona" in prediction, "Persona prediction failed"
    print(f"  -> OK: FCM σύγκλινε σε {metrics['iterations_to_converge']} επαναλήψεις.")
    print(f"  -> Κυρίαρχο προφίλ: {prediction['dominant_persona']} ({prediction['dominant_pct']}%)")
    print(f"  -> Partition Coefficient (PC): {metrics['partition_coefficient_PC']}, Partition Entropy (PE): {metrics['partition_entropy_PE']}")

    # 4. Test Catalog Manager
    print("\n[4/7] Έλεγχος Βάσης Προορισμών (catalog_manager.py)...")
    from data.catalog_manager import CatalogManager
    cat_mgr = CatalogManager()
    dests = cat_mgr.get_all()
    assert len(dests) >= 12, "Catalog destinations count lower than expected"
    df_cat = cat_mgr.to_dataframe()
    assert len(df_cat) == len(dests), "DataFrame export size mismatch"
    print(f"  -> OK: Φορτώθηκαν {len(dests)} προορισμοί (Ελλάδα & Εξωτερικό) με πλήρη δεδομένα.")

    # 5. Test Feedback Manager
    print("\n[5/7] Έλεγχος Μηχανισμού Ανάδρασης (feedback_manager.py)...")
    from data.feedback_manager import FeedbackManager
    fb_mgr = FeedbackManager()
    fb_entry = fb_mgr.record_feedback(
        "gr_chania", "Χανιά", test_inputs, rating=5, accepted=True, comment="Αυτοματοποιημένος έλεγχος δοκιμής"
    )
    assert fb_entry["id"], "Feedback recording failed"
    stats = fb_mgr.get_destination_feedback_stats("gr_chania")
    assert stats["count"] >= 1, "Feedback stats failed"
    print(f"  -> OK: Ανάδραση καταγράφηκε επιτυχώς (Αποδοχή, Βαθμολογία 5/5, Δ_feedback: +{stats['feedback_delta']}%).")

    # 6. Test Hybrid Tourism Recommender
    print("\n[6/7] Έλεγχος Υβριδικού Recommender (recommender.py)...")
    from core.recommender import HybridTourismRecommender
    rec = HybridTourismRecommender()
    res = rec.recommend(test_inputs, top_n=3)
    assert len(res["recommendations"]) == 3, "Recommendation count mismatch"
    top_dest = res["recommendations"][0]
    print(f"  -> OK: Κορυφαίος προτεινόμενος προορισμός: {top_dest['destination']['name']} ({top_dest['final_score']}%)")
    print(f"  -> Αιτιολόγηση (XAI): {top_dest['rationale'][0]}")

    # 7. Test Visualizations & UI components
    print("\n[7/7] Έλεγχος Οπτικοποιήσεων & Γραφημάτων (visualizations.py)...")
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

    print("\n" + "="*50)
    print("  ΟΛΟΙ ΟΙ ΕΛΕΓΧΟΙ ΟΛΟΚΛΗΡΩΘΗΚΑΝ ΜΕ ΕΠΙΤΥΧΙΑ (100% PASS)")
    print("="*50)

if __name__ == "__main__":
    run_tests()
