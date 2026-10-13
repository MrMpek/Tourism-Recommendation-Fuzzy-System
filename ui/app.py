"""
FuzzyTravel AI - Intelligent Decision Support System for Tourism Recommendations.
Academic Master's Project & B2B Commercial Advisory Prototype.
"""
import os
import sys

# Ensure root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from core.recommender import HybridTourismRecommender
from data.catalog_manager import CatalogManager
from docs.generate_proposal_pdf import create_travel_proposal_pdf
from ui.visualizations import (
    plot_fuzzy_variable,
    plot_persona_radar_chart,
    plot_destination_scores_breakdown,
    plot_active_rules_chart
)

# Page configuration
st.set_page_config(
    page_title="FuzzyTravel AI | Έμπειρο Σύστημα Τουριστικών Προτάσεων",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3799;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #576574;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #1e3799;
        margin-bottom: 10px;
    }
    .dest-card {
        background: white;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        border: 1px solid #eef2f5;
        margin-bottom: 20px;
    }
    .badge-primary {
        background-color: #e8f0fe;
        color: #1a73e8;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-success {
        background-color: #e6f4ea;
        color: #137333;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_recommender():
    return HybridTourismRecommender()


recommender = get_recommender()
catalog_mgr = recommender.catalog_mgr

# Sidebar Navigation
st.sidebar.image("https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=400&q=80", width="stretch")
st.sidebar.title("🧭 Πλοήγηση")
app_mode = st.sidebar.radio(
    "Επιλέξτε Λειτουργία:",
    [
        "✈️ Σύμβουλος Προτάσεων (Travel Agent Recommender)",
        "🧠 Ασαφής Μηχανή & FCM (Ακαδημαϊκή Εποπτεία)",
        "💼 Διαχείριση Καταλόγου & Πακέτων (B2B Inventory)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Εργασία Μεταπτυχιακού 2026**")
st.sidebar.caption("Μάθημα: Ασαφή Συστήματα & Υπολογιστική Νοημοσύνη")

# ==============================================================================
# MODE 1: TRAVEL AGENT RECOMMENDER
# ==============================================================================
if app_mode == "✈️ Σύμβουλος Προτάσεων (Travel Agent Recommender)":
    st.markdown('<div class="main-title">FuzzyTravel AI — Σύστημα Εξατομικευμένων Προτάσεων</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Υβριδικός μηχανισμός Mamdani Fuzzy Inference & Fuzzy C-Means (FCM) Soft Personas για τουριστικά γραφεία.</div>', unsafe_allow_html=True)

    col_inputs, col_results = st.columns([1, 2], gap="large")

    with col_inputs:
        st.subheader("📋 Παράμετροι Πελάτη")

        st.markdown("##### 1. Βασικά Στοιχεία Ταξιδιού")
        budget = st.slider("Προϋπολογισμός (€/άτομο)", min_value=150, max_value=5000, value=1200, step=50, help="Συνολικός προϋπολογισμός ταξιδιού")
        climate = st.slider("Προτιμώμενη Θερμοκρασία (°C)", min_value=-5, max_value=40, value=25, step=1, help="Επιθυμητή μέση θερμοκρασία προορισμού")
        duration = st.slider("Διάρκεια Ταξιδιού (Ημέρες)", min_value=1, max_value=25, value=5, step=1, help="Αριθμός ημερών διαμονής")

        st.markdown("##### 2. Ενδιαφέροντα & Δραστηριότητες (0-10)")
        culture = st.slider("🏛️ Πολιτισμός, Ιστορία & Μουσεία", 0.0, 10.0, 7.5, 0.5)
        adventure = st.slider("🏔️ Περιπέτεια, Φύση & Outdoors", 0.0, 10.0, 4.0, 0.5)
        relaxation = st.slider("🏖️ Χαλάρωση, Παραλίες & Wellness", 0.0, 10.0, 8.0, 0.5)
        nightlife = st.slider("🍸 Νυχτερινή Ζωή & Διασκέδαση", 0.0, 10.0, 6.0, 0.5)

        st.markdown("##### 3. Φίλτρα")
        all_countries = ["Όλες"] + sorted(list(set(d.get("country", "") for d in catalog_mgr.get_all())))
        country_filter = st.selectbox("Χώρα Προορισμού", all_countries, index=0)

        user_query = {
            "budget": float(budget),
            "climate": float(climate),
            "duration": float(duration),
            "culture": float(culture),
            "adventure": float(adventure),
            "relaxation": float(relaxation),
            "nightlife": float(nightlife)
        }

    # Execute Recommendation
    results = recommender.recommend(user_query, top_n=5, country_filter=country_filter)
    fcm_data = results["fcm_profiling"]
    top_destinations = results["recommendations"]

    with col_results:
        # Top Metrics & Profiling Header
        st.subheader("🎯 Ανάλυση Προφίλ Πελάτη (FCM)")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Κυρίαρχο Προφίλ (FCM)", fcm_data["dominant_persona"])
        with m2:
            st.metric("Βαθμός Ταύτισης", f"{fcm_data['dominant_pct']}%")
        with m3:
            st.metric("Κορυφαίο Ταίριασμα", f"{top_destinations[0]['final_score']}%" if top_destinations else "N/A")
        with m4:
            st.metric("Ενεργοί Κανόνες", f"{len(results['active_fuzzy_rules'])}")

        # Radar Persona Chart expander
        with st.expander("📊 Προβολή Πολυδιάστατου Προφίλ Ταξιδιώτη (FCM Soft Persona Radar)", expanded=False):
            st.plotly_chart(plot_persona_radar_chart(fcm_data["all_personas"]), use_container_width=True)

        # B2B Client Quotation PDF Export
        with st.expander("📄 Εξαγωγή Επίσημης Ταξιδιωτικής Προσφοράς σε PDF (B2B Client Quotation)", expanded=False):
            st.markdown("Δημιουργήστε ένα επαγγελματικό, επίσημο έντυπο προσφοράς PDF για άμεση αποστολή στον πελάτη:")
            pq_c1, pq_c2 = st.columns(2)
            with pq_c1:
                client_name = st.text_input("Ονοματεπώνυμο Πελάτη", "Ιωάννης Παπαδόπουλος", key="prop_client_name")
            with pq_c2:
                agent_name = st.text_input("Ταξιδιωτικός Σύμβουλος", "FuzzyTravel AI Specialist", key="prop_agent_name")
            proposal_notes = st.text_area(
                "Ειδικές Σημειώσεις / Παρατηρήσεις Προσφοράς",
                "Η προσφορά περιλαμβάνει διαμονή σε 4* / boutique ξενοδοχείο, πρωινό, ιδιωτική μεταφορά και 24/7 υποστήριξη concierge. Ισχύει για κράτηση εντός 7 ημερών.",
                key="prop_notes"
            )
            if top_destinations:
                proposal_pdf = create_travel_proposal_pdf(
                    client_name=client_name,
                    agent_name=agent_name,
                    user_query=user_query,
                    fcm_data=fcm_data,
                    recommendations=top_destinations,
                    proposal_notes=proposal_notes
                )
                safe_client_name = "".join(c for c in client_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
                st.download_button(
                    label=f"📥 Λήψη Επίσημης Προσφοράς (PDF) για {client_name}",
                    data=proposal_pdf,
                    file_name=f"Travel_Proposal_{safe_client_name or 'Client'}.pdf",
                    mime="application/pdf",
                    type="primary",
                    key="btn_download_proposal_pdf"
                )

        st.subheader("🏆 Κορυφαίες Εξατομικευμένες Προτάσεις")

        if not top_destinations:
            st.warning("Δεν βρέθηκαν προορισμοί με τα συγκεκριμένα κριτήρια. Δοκιμάστε να αλλάξετε το φίλτρο χώρας.")
        else:
            for rank, rec in enumerate(top_destinations, 1):
                dest = rec["destination"]
                score = rec["final_score"]
                est_cost = rec["estimated_trip_cost"]

                with st.container():
                    st.markdown(f"""
                    <div class="dest-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; color: #2c3e50;">#{rank}. {dest['name']} ({dest['country']})</h3>
                            <span class="badge-success" style="font-size: 1.05rem;">Συνολικό Ταίριασμα: {score}%</span>
                        </div>
                        <p style="margin-top: 5px; color: #7f8c8d; font-size: 0.95rem;">
                            <strong>Περιφέρεια:</strong> {dest.get('region', '')} | 
                            <strong>Τύπος:</strong> <span class="badge-primary">{dest.get('archetype', '')}</span> |
                            <strong>Εποχή:</strong> {dest.get('best_season', '')}
                        </p>
                        <p style="font-size: 0.95rem; color: #34495e;">{dest.get('description', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    c_img, c_details = st.columns([1, 2])
                    with c_img:
                        if dest.get("image_url"):
                            try:
                                st.image(dest["image_url"], caption=dest["name"])
                            except Exception:
                                st.caption(f"📍 {dest['name']}")
                        st.caption(f"💰 Εκτιμώμενο Κόστος: ~{est_cost}€ / άτομο")

                    with c_details:
                        st.markdown(f"**📦 Προτεινόμενο Πακέτο Γραφείου:** `{dest.get('agency_package', 'Standard Explorer Package')}`")
                        
                        # Breakdown Chart
                        st.plotly_chart(
                            plot_destination_scores_breakdown(rec["component_scores"], dest["name"]),
                            key=f"breakdown_{dest.get('id', str(rank))}_{rank}"
                        )

                        # Explainability Rationale
                        st.markdown("**💡 Αιτιολόγηση Συστήματος (Explainable AI):**")
                        for reason in rec["rationale"]:
                            st.markdown(f"- ✅ {reason}")

                        with st.expander("✨ Κορυφαία Αξιοθέατα & Εμπειρίες"):
                            for h in dest.get("highlights", []):
                                st.markdown(f"• {h}")

                        # Interactive Feedback Loop
                        with st.expander("🔄 Ανάδραση Χρήστη για την Πρόταση (Feedback Loop)"):
                            f_col1, f_col2 = st.columns([1, 1])
                            with f_col1:
                                fb_rating = st.select_slider(
                                    "Βαθμολογία Πρότασης:",
                                    options=[1, 2, 3, 4, 5],
                                    value=5,
                                    format_func=lambda x: f"{x} ⭐",
                                    key=f"star_{dest['id']}_{rank}"
                                )
                                fb_accepted = st.radio(
                                    "Απόφαση:",
                                    ["👍 Αποδοχή Πρότασης", "👎 Απόρριψη"],
                                    horizontal=True,
                                    key=f"acc_{dest['id']}_{rank}"
                                )
                            with f_col2:
                                fb_comment = st.text_input(
                                    "Σχόλιο / Παρατήρηση:",
                                    placeholder="π.χ. Ιδανικό για την εποχή",
                                    key=f"comm_{dest['id']}_{rank}"
                                )
                                if st.button("📩 Υποβολή Ανάδρασης", key=f"btn_fb_{dest['id']}_{rank}"):
                                    is_acc = "Αποδοχή" in fb_accepted
                                    recommender.record_feedback(
                                        dest["id"],
                                        dest["name"],
                                        user_query,
                                        fb_rating,
                                        is_acc,
                                        fb_comment
                                    )
                                    st.success("✅ Η ανάδραση καταχωρήθηκε! Το σύστημα αναπροσαρμόζει αυτόματα τα βάρη.")

                    st.markdown("---")

# ==============================================================================
# MODE 2: FUZZY ENGINE & FCM INSPECTOR (ACADEMIC VIEW)
# ==============================================================================
elif app_mode == "🧠 Ασαφής Μηχανή & FCM (Ακαδημαϊκή Εποπτεία)":
    st.markdown('<div class="main-title">Ακαδημαϊκή Εποπτεία & Μαθηματικό Υπόβαθρο</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Λεπτομερής επισκόπηση των Ασαφών Συνόλων, των Κανόνων IF-THEN, της Αποσαφοποίησης και του Αλγορίθμου Fuzzy C-Means.</div>', unsafe_allow_html=True)

    tab_mf, tab_rules, tab_fcm, tab_feedback = st.tabs([
        "📈 1. Συναρτήσεις Συμμετοχής (Membership Functions)",
        "📜 2. Βάση Ασαφών Κανόνων & Firing Strengths",
        "🔬 3. Αλγόριθμος Fuzzy C-Means (Bezdek)",
        "🔄 4. Μηχανισμός Ανάδρασης (Feedback Loop)"
    ])

    with tab_mf:
        st.markdown("### 📊 Ορισμός Ασαφών Μεταβλητών & Συναρτήσεων Συμμετοχής")
        st.write("Το σύστημα χρησιμοποιεί τριγωνικές και τραπεζοειδείς συναρτήσεις συμμετοχής για να μοντελοποιήσει τις ανθρώπινες προτιμήσεις:")

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(plot_fuzzy_variable(recommender.fuzzy_engine.var_budget, 1200), use_container_width=True)
            st.plotly_chart(plot_fuzzy_variable(recommender.fuzzy_engine.var_duration, 5), use_container_width=True)
            st.plotly_chart(plot_fuzzy_variable(recommender.fuzzy_engine.var_culture, 7.5), use_container_width=True)
            st.plotly_chart(plot_fuzzy_variable(recommender.fuzzy_engine.var_relaxation, 8.0), use_container_width=True)

        with c2:
            st.plotly_chart(plot_fuzzy_variable(recommender.fuzzy_engine.var_climate, 25), use_container_width=True)
            st.plotly_chart(plot_fuzzy_variable(recommender.fuzzy_engine.var_suitability, 75), use_container_width=True)
            st.plotly_chart(plot_fuzzy_variable(recommender.fuzzy_engine.var_adventure, 4.0), use_container_width=True)
            st.plotly_chart(plot_fuzzy_variable(recommender.fuzzy_engine.var_nightlife, 6.0), use_container_width=True)

    with tab_rules:
        st.markdown("### 📜 Βάση Ασαφών Κανόνων (Mamdani Fuzzy Rule Base)")
        st.write(f"Συνολικά ορίζονται **{len(recommender.fuzzy_engine.rules)} κανόνες εμπειρογνώμονα** που συνδυάζουν τις εισόδους με τύπους προορισμών και βαθμούς καταλληλότητας (Poor, Moderate, High, Excellent):")

        rules_data = []
        for r in recommender.fuzzy_engine.rules:
            ante_str = " AND ".join([f"{k} = {v}" for k, v in r.antecedent.items()])
            conseq_str = f"Archetype: {r.consequent.get('archetype')}, Suitability: {r.consequent.get('suitability')}"
            rules_data.append({
                "Rule ID": r.rule_id,
                "IF (Υπόθεση)": ante_str,
                "THEN (Συμπέρασμα)": conseq_str,
                "Περιγραφή": r.description
            })

        df_rules = pd.DataFrame(rules_data)
        st.dataframe(df_rules, width="stretch", height=450)

        st.markdown("#### Μέθοδος Αποσαφοποίησης (Centroid / Center of Gravity)")
        st.latex(r"z^* = \frac{\int z \cdot \mu_A(z) \, dz}{\int \mu_A(z) \, dz} \approx \frac{\sum_{i=1}^n z_i \cdot \mu_A(z_i)}{\sum_{i=1}^n \mu_A(z_i)}")
        st.info("Υπολογίζεται το κέντρο βάρους του συνενωμένου (aggregated) ασαφούς συνόλου εξόδου για κάθε αρχέτυπο προορισμού. Σε περίπτωση μη ενεργοποίησης κανόνα, αποδίδεται χαμηλό σκορ βάσης 10.0%.")

    with tab_fcm:
        st.markdown("### 🔬 Μαθηματική Διατύπωση Fuzzy C-Means (FCM)")
        st.info("ℹ️ **Συνθετικό Σύνολο Δεδομένων (Synthetic Dataset):** Το dataset εκπαίδευσης του FCM αποτελείται από 350 συνθετικά δείγματα ταξιδιωτών που μοντελοποιούν ρεαλιστικά ταξιδιωτικά μοτίβα και καταναλωτικά προφίλ στην Ελλάδα και διεθνώς.")
        st.write("Ο αλγόριθμος Fuzzy C-Means (Bezdek 1981) ελαχιστοποιεί τη συνάρτηση κόστους:")
        st.latex(r"J_m = \sum_{i=1}^N \sum_{j=1}^C (u_{ij})^m \cdot \|x_i - v_j\|^2")
        st.write("Όπου:")
        st.markdown(r"""
        * $N$: Πλήθος ταξιδιωτών ιστορικού ($N = 350$)
        * $C$: Πλήθος συστάδων / τουριστικών personas ($C = 5$)
        * $m$: Συντελεστής ασάφειας (fuzzifier, $m = 2.0$)
        * $u_{ij} \in [0, 1]$: Βαθμός συμμετοχής του χρήστη $i$ στην ομάδα $j$, με $\sum_{j=1}^C u_{ij} = 1$
        * $v_j$: Κεντροειδές της συστάδας $j$ (ευθυγραμμισμένο μέσω του αλγορίθμου Hungarian - Kuhn-Munkres)
        """)

        metrics = recommender.fcm_model.compute_validation_metrics()
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Partition Coefficient (PC)", metrics.get("partition_coefficient_PC", 0.0), help="Μέτρο ευκρίνειας των συστάδων (1/C <= PC <= 1, υψηλότερο είναι καλύτερο)")
        with col_m2:
            st.metric("Partition Entropy (PE)", metrics.get("partition_entropy_PE", 0.0), help="Μέτρο αβεβαιότητας διαμέρισης (0 <= PE <= log(C), χαμηλότερο είναι καλύτερο)")
        with col_m3:
            st.metric("Επαναλήψεις Σύγκλισης", metrics.get("iterations_to_converge", 0))

        st.markdown("#### 📍 Πίνακας Κεντροειδών Προφίλ σε Φυσικές Μονάδες (€, °C, Ημέρες, 0-10)")
        df_centroids = recommender.fcm_model.get_centroids_dataframe()
        st.dataframe(df_centroids, width="stretch")

        # Cost function convergence plot
        fig_cost = px.line(
            x=list(range(1, len(recommender.fcm_model.cost_history) + 1)),
            y=recommender.fcm_model.cost_history,
            labels={"x": "Επανάληψη (Iteration)", "y": "Αντικειμενική Συνάρτηση J_m"},
            title="Καμπύλη Σύγκλισης FCM (Objective Function J_m)"
        )
        fig_cost.update_layout(template="plotly_white", height=320)
        st.plotly_chart(fig_cost, use_container_width=True)


    with tab_feedback:
        st.markdown("### 🔄 Μηχανισμός Ανάδρασης & Προσαρμοστική Μάθηση (Closed Feedback Loop)")
        st.write("Σύμφωνα με τις προδιαγραφές της εργασίας, το σύστημα περιλαμβάνει πλήρη βρόχο ανάδρασης (Feedback Loop):")
        
        st.markdown(r"""
        * **1. Συλλογή Ανάδρασης:** Ο χρήστης/πράκτορας αξιολογεί τις προτάσεις (1-5 αστέρια, Αποδοχή/Απόρριψη, σχόλιο).
        * **2. Προσαρμογή Βαρών (Adaptive Adjustment):** 
        """)
        st.latex(r"\Delta_{\text{feedback}} = w_r \cdot (\bar{r} - 3.0) + w_a \cdot (\text{acceptance\_rate} - 0.5)")
        st.markdown(r"""
        Όπου $\bar{r}$ είναι ο μέσος όρος αστεριών και $\text{acceptance\_rate}$ το ποσοστό επιλογής. Προορισμοί με συνεπή θετική ανάδραση λαμβάνουν προσαρμογή έως +10%, ενώ απορριφθείσες επιλογές υποβαθμίζονται αυτόματα.
        * **3. Επεξηγησιμότητα (XAI):** Η επίδραση της ανάδρασης αναφέρεται ρητά στην αιτιολόγηση της τελικής πρότασης.
        """)

        fb_summary = recommender.feedback_mgr.get_overall_summary()
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            st.metric("Συνολικές Αξιολογήσεις Χρηστών", fb_summary["total_feedbacks"])
        with col_f2:
            st.metric("Μέση Βαθμολογία Προτάσεων", f"{fb_summary['avg_rating']} ⭐" if fb_summary["total_feedbacks"] > 0 else "N/A")
        with col_f3:
            st.metric("Ποσοστό Αποδοχής Προτάσεων", f"{fb_summary['acceptance_rate']}%" if fb_summary["total_feedbacks"] > 0 else "N/A")

        st.markdown("#### 📜 Ιστορικό Καταγεγραμμένης Ανάδρασης (Feedback Log)")
        all_fb = recommender.feedback_mgr.feedback_entries
        if all_fb:
            df_fb = pd.DataFrame([
                {
                    "Ημερομηνία": e["timestamp"][:19].replace("T", " "),
                    "Προορισμός": e["destination_name"],
                    "Βαθμολογία": f"{e['rating']} ⭐",
                    "Απόφαση": "👍 Αποδοχή" if e["accepted"] else "👎 Απόρριψη",
                    "Σχόλιο": e.get("comment", ""),
                    "Budget Χρήστη": f"{int(e['user_query'].get('budget', 0))}€",
                    "Θερμοκρασία": f"{int(e['user_query'].get('climate', 0))}°C"
                }
                for e in reversed(all_fb)
            ])
            st.dataframe(df_fb, width="stretch")
        else:
            st.info("💡 Δεν υπάρχουν ακόμη καταγεγραμμένες αξιολογήσεις. Μεταβείτε στην καρτέλα '✈️ Σύμβουλος Προτάσεων' και υποβάλετε ανάδραση σε έναν προορισμό για να τη δείτε ζωντανά εδώ!")

# ==============================================================================
# MODE 3: B2B INVENTORY & CATALOG MANAGEMENT
# ==============================================================================
elif app_mode == "💼 Διαχείριση Καταλόγου & Πακέτων (B2B Inventory)":
    st.markdown('<div class="main-title">Διαχείριση Καταλόγου Προορισμών & Πακέτων Γραφείου</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Εμπορική διαχείριση ταξιδιωτικού αποθέματος, εισαγωγή νέων πακέτων και εξαγωγή δεδομένων.</div>', unsafe_allow_html=True)

    df_cat = catalog_mgr.to_dataframe()
    st.dataframe(df_cat, width="stretch", height=350)

    # Download CSV
    csv_bytes = df_cat.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📥 Εξαγωγή Καταλόγου σε CSV",
        data=csv_bytes,
        file_name="travel_catalog_inventory.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("➕ Προσθήκη Νέου Προορισμού / Ταξιδιωτικού Πακέτου")

    with st.form("new_destination_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_id = st.text_input("ID Προορισμού (π.χ. gr_rhodes)", "gr_rhodes")
            new_name = st.text_input("Όνομα Προορισμού", "Ρόδος")
            new_country = st.text_input("Χώρα", "Ελλάδα")
            new_region = st.text_input("Περιφέρεια", "Δωδεκάνησα")
        with c2:
            new_arch = st.selectbox("Κύριος Τύπος Προορισμού", [
                "Coastal & Island Relaxation",
                "Cultural & Heritage City",
                "Alpine & Mountain Adventure",
                "Luxury & Premium Wellness",
                "Vibrant Urban & Entertainment",
                "Exotic & Tropical Explorer"
            ])
            new_cost = st.number_input("Μέσο Ημερήσιο Κόστος (€)", min_value=30, max_value=1500, value=120)
            new_temp = st.number_input("Τυπική Θερμοκρασία (°C)", min_value=-15, max_value=45, value=28)
            new_season = st.text_input("Ιδανική Εποχή", "Μάιος - Οκτώβριος")
        with c3:
            s_cult = st.slider("Culture Score (0-10)", 0.0, 10.0, 8.0, 0.5)
            s_adv = st.slider("Adventure Score (0-10)", 0.0, 10.0, 5.0, 0.5)
            s_rel = st.slider("Relaxation Score (0-10)", 0.0, 10.0, 9.0, 0.5)
            s_night = st.slider("Nightlife Score (0-10)", 0.0, 10.0, 7.5, 0.5)

        new_desc = st.text_area("Περιγραφή", "Μεσαιωνική πόλη Ιπποτών, παραλίες και πολυτελή resorts.")
        new_pkg = st.text_input("Τίτλος Πακέτου Γραφείου", "Rhodes Knights & Emerald Coast (6D/5N)")
        new_img = st.text_input("URL Εικόνας", "https://images.unsplash.com/photo-1594918731553-73138b725c48?auto=format&fit=crop&w=800&q=80")

        save_btn = st.form_submit_button("💾 Αποθήκευση στον Κατάλογο", type="primary")

        if save_btn:
            new_dest_record = {
                "id": new_id,
                "name": new_name,
                "country": new_country,
                "region": new_region,
                "archetype": new_arch,
                "secondary_archetype": "Cultural & Heritage City",
                "avg_daily_cost": int(new_cost),
                "budget_tier": "Medium" if new_cost < 200 else "High",
                "optimal_duration_days": [4, 8],
                "typical_temperature_c": int(new_temp),
                "climate_label": "Warm" if new_temp >= 22 else "Mild",
                "scores": {
                    "culture": float(s_cult),
                    "adventure": float(s_adv),
                    "relaxation": float(s_rel),
                    "nightlife": float(s_night)
                },
                "description": new_desc,
                "best_season": new_season,
                "highlights": ["Μεσαιωνική Πόλη Ρόδου", "Λίνδος & Ακρόπολη", "Κοιλάδα των Πεταλούδων"],
                "agency_package": new_pkg,
                "image_url": new_img
            }
            catalog_mgr.add_destination(new_dest_record)
            st.success(f"Ο προορισμός '{new_name}' προστέθηκε επιτυχώς στη βάση δεδομένων!")
            st.rerun()
