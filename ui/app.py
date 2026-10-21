"""
Fuzzy Travel Recommendation System.
Decision support system using Mamdani Fuzzy Inference & Fuzzy C-Means clustering.
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
    page_title="Σύστημα τουριστικών προτάσεων με ασαφή λογική",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (minimal, clean technical design)
st.markdown("""
<style>
    .main-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .dest-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .badge-score {
        background-color: #f8fafc;
        color: #0f172a;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.9rem;
        font-weight: 600;
        border: 1px solid #cbd5e1;
    }
    .badge-arch {
        background-color: #f1f5f9;
        color: #475569;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        border: 1px solid #e2e8f0;
    }
    /* Σαφή πλαίσια σε όλα τα πλήκτρα (κουμπιά) */
    div.stButton > button,
    div.stDownloadButton > button,
    div[data-testid="stFormSubmitButton"] > button,
    button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-primary"] {
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 0.45rem 1rem !important;
        transition: all 0.15s ease-in-out !important;
    }
    div.stButton > button,
    div.stDownloadButton > button,
    button[data-testid="baseButton-secondary"] {
        border: 1.5px solid #94a3b8 !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }
    div.stButton > button:hover,
    div.stDownloadButton > button:hover,
    button[data-testid="baseButton-secondary"]:hover {
        border-color: #334155 !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }
    div.stButton > button[kind="primary"],
    div.stDownloadButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button,
    button[data-testid="baseButton-primary"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1.5px solid #0f172a !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stDownloadButton > button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    button[data-testid="baseButton-primary"]:hover {
        background-color: #334155 !important;
        border-color: #0f172a !important;
        color: #ffffff !important;
    }
    /* Διακριτικό πλαίσιο στα expanders */
    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
        background: #ffffff !important;
    }
    /* Απόκρυψη προεπιλεγμένου κουμπιού Deploy του Streamlit */
    .stDeployButton, [data-testid="stAppDeployButton"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_recommender():
    return HybridTourismRecommender()


recommender = get_recommender()
catalog_mgr = recommender.catalog_mgr

MODE_RECOMMENDER = "Σύμβουλος προτάσεων"
MODE_ACADEMIC = "Ασαφής μηχανή & FCM"
MODE_INVENTORY = "Διαχείριση καταλόγου"

MODES = [MODE_RECOMMENDER, MODE_ACADEMIC, MODE_INVENTORY]


def normalize_mode(val):
    s = str(val)
    for e in ["✈️ ", "🧠 ", "💼 ", "✈️", "🧠", "💼"]:
        s = s.replace(e, "").strip()
    s = s.replace(" (Travel Agent Recommender)", "").replace(" (Ακαδημαϊκή Εποπτεία)", "").replace(" & Πακέτων (B2B Inventory)", "")
    s_lower = s.lower()
    if "προτάσεων" in s_lower or "recommender" in s_lower:
        return MODE_RECOMMENDER
    if "ασαφής" in s_lower or "fcm" in s_lower or "εποπτεία" in s_lower:
        return MODE_ACADEMIC
    if "καταλόγου" in s_lower or "inventory" in s_lower:
        return MODE_INVENTORY
    return s


# Sidebar Navigation
st.sidebar.title("Πλοήγηση")
raw_app_mode = st.sidebar.radio(
    "Επιλογή λειτουργίας:",
    MODES,
    format_func=normalize_mode
)
app_mode = normalize_mode(raw_app_mode)

st.sidebar.markdown("---")
st.sidebar.markdown("**Εργασία Μεταπτυχιακού 2026**")
st.sidebar.caption("Μάθημα: Τεχνολογία Ασαφών Συστημάτων Λογισμικού")

# ==============================================================================
# MODE 1: RECOMMENDER
# ==============================================================================
if app_mode == MODE_RECOMMENDER:
    st.markdown('<div class="main-title">Σύστημα τουριστικών προτάσεων με ασαφή λογική</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Υβριδικός μηχανισμός ασαφούς συμπερασμού (Mamdani FIS) και ομαδοποίησης χρηστών (Fuzzy C-Means).</div>', unsafe_allow_html=True)

    col_inputs, col_results = st.columns([1, 2], gap="large")

    with col_inputs:
        st.subheader("Παράμετροι εισόδου")

        st.markdown("##### Βασικά στοιχεία ταξιδιού")
        budget = st.slider("Προϋπολογισμός (€/άτομο)", min_value=150, max_value=5000, value=1200, step=50, help="Συνολικός προϋπολογισμός ταξιδιού")
        climate = st.slider("Προτιμώμενη θερμοκρασία (°C)", min_value=-5, max_value=40, value=25, step=1, help="Επιθυμητή μέση θερμοκρασία προορισμού")
        duration = st.slider("Διάρκεια ταξιδιού (ημέρες)", min_value=1, max_value=25, value=5, step=1, help="Αριθμός ημερών διαμονής")

        st.markdown("##### Ενδιαφέροντα & δραστηριότητες (0-10)")
        culture = st.slider("Πολιτισμός, ιστορία & μουσεία", 0.0, 10.0, 7.5, 0.5)
        adventure = st.slider("Περιπέτεια, φύση & ύπαιθρος", 0.0, 10.0, 4.0, 0.5)
        relaxation = st.slider("Χαλάρωση, παραλίες & ευεξία", 0.0, 10.0, 8.0, 0.5)
        nightlife = st.slider("Νυχτερινή ζωή & διασκέδαση", 0.0, 10.0, 6.0, 0.5)

        st.markdown("##### Φίλτρα")
        all_countries = ["Όλες"] + sorted(list(set(d.get("country", "") for d in catalog_mgr.get_all())))
        country_filter = st.selectbox("Χώρα προορισμού", all_countries, index=0)

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
        st.subheader("Προφίλ χρήστη (Fuzzy C-Means)")
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Κυρίαρχο προφίλ", fcm_data["dominant_persona"])
        with m2:
            st.metric("Βαθμός ταύτισης", f"{fcm_data['dominant_pct']}%")

        with st.expander("Στοιχεία υπολογισμού", expanded=False):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.metric("Κορυφαία βαθμολογία", f"{top_destinations[0]['final_score']}%" if top_destinations else "N/A")
            with col_e2:
                st.metric("Ενεργοποιημένοι κανόνες", f"{len(results['active_fuzzy_rules'])}")

        with st.expander("Κατανομή συμμετοχής σε προφίλ (FCM Radar)", expanded=False):
            st.plotly_chart(plot_persona_radar_chart(fcm_data["all_personas"]), use_container_width=True)

        with st.expander("Εξαγωγή πρότασης σε PDF", expanded=False):
            st.markdown("Δημιουργία τεχνικού εντύπου πρότασης σε μορφή PDF:")
            pq_c1, pq_c2 = st.columns(2)
            with pq_c1:
                client_name = st.text_input("Ονοματεπώνυμο", "Ιωάννης Παπαδόπουλος", key="prop_client_name")
            with pq_c2:
                agent_name = st.text_input("Σύμβουλος", "Σύμβουλος FuzzyTravel", key="prop_agent_name")
            proposal_notes = st.text_area(
                "Σημειώσεις πρότασης",
                "Η προσφορά περιλαμβάνει διαμονή, πρωινό και μεταφορά. Ισχύει για κράτηση εντός 7 ημερών.",
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
                    label=f"Λήψη πρότασης (PDF) για {client_name}",
                    data=proposal_pdf,
                    file_name=f"Travel_Proposal_{safe_client_name or 'Client'}.pdf",
                    mime="application/pdf",
                    type="primary",
                    key="btn_download_proposal_pdf"
                )

        st.subheader("Προτάσεις προορισμών")

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
                            <h4 style="margin: 0; color: #0f172a;">#{rank}. {dest['name']} ({dest['country']})</h4>
                            <span class="badge-score">Βαθμολογία: {score}%</span>
                        </div>
                        <p style="margin: 4px 0 6px 0; color: #64748b; font-size: 0.85rem;">
                            Περιφέρεια: {dest.get('region', '')} | 
                            Τύπος: <span class="badge-arch">{dest.get('archetype', '')}</span> |
                            Ιδανική εποχή: {dest.get('best_season', '')} |
                            Εκτιμώμενο κόστος: ~{est_cost} €
                        </p>
                        <p style="margin: 0; font-size: 0.9rem; color: #334155;">{dest.get('description', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    c_img, c_details = st.columns([1, 2])
                    with c_img:
                        if dest.get("image_url"):
                            try:
                                st.image(dest["image_url"], caption=dest["name"])
                            except Exception:
                                st.caption(dest['name'])

                    with c_details:
                        st.markdown("**Αιτιολόγηση:**")
                        for reason in rec["rationale"][:2]:
                            st.markdown(f"- {reason}")

                        with st.expander("Αναλυτική βαθμολογία", expanded=False):
                            if len(rec["rationale"]) > 2:
                                for reason in rec["rationale"][2:]:
                                    st.markdown(f"- {reason}")
                            st.caption(f"Προτεινόμενο πακέτο: {dest.get('agency_package', 'Standard Package')}")
                            st.plotly_chart(
                                plot_destination_scores_breakdown(rec["component_scores"], dest["name"]),
                                key=f"breakdown_{dest.get('id', str(rank))}_{rank}",
                                use_container_width=True
                            )

                        with st.expander("Αξιοθέατα & δραστηριότητες", expanded=False):
                            for h in dest.get("highlights", []):
                                st.markdown(f"- {h}")

                        with st.expander("Ανάδραση", expanded=False):
                            f_col1, f_col2 = st.columns([1, 1])
                            with f_col1:
                                fb_rating = st.select_slider(
                                    "Βαθμολογία:",
                                    options=[1, 2, 3, 4, 5],
                                    value=5,
                                    format_func=lambda x: f"{x}/5",
                                    key=f"star_{dest['id']}_{rank}"
                                )
                                fb_accepted = st.radio(
                                    "Απόφαση:",
                                    ["Αποδοχή", "Απόρριψη"],
                                    horizontal=True,
                                    key=f"acc_{dest['id']}_{rank}"
                                )
                            with f_col2:
                                fb_comment = st.text_input(
                                    "Σχόλιο:",
                                    placeholder="π.χ. Καλή επιλογή για την εποχή",
                                    key=f"comm_{dest['id']}_{rank}"
                                )
                                if st.button("Υποβολή ανάδρασης", key=f"btn_fb_{dest['id']}_{rank}"):
                                    is_acc = "Αποδοχή" in fb_accepted
                                    recommender.record_feedback(
                                        dest["id"],
                                        dest["name"],
                                        user_query,
                                        fb_rating,
                                        is_acc,
                                        fb_comment
                                    )
                                    st.success("Η ανάδραση καταχωρήθηκε.")

                    st.markdown("---")

# ==============================================================================
# MODE 2: FUZZY ENGINE & FCM INSPECTOR (ACADEMIC VIEW)
# ==============================================================================
elif app_mode == MODE_ACADEMIC:
    st.markdown('<div class="main-title">Ασαφής Μηχανή & FCM</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Συναρτήσεις συμμετοχής, βάση κανόνων IF-THEN, μέθοδος αποσαφοποίησης και αλγόριθμος Fuzzy C-Means.</div>', unsafe_allow_html=True)

    tab_mf, tab_rules, tab_fcm, tab_feedback = st.tabs([
        "Συναρτήσεις συμμετοχής",
        "Βάση κανόνων",
        "Fuzzy C-Means",
        "Ανάδραση"
    ])

    with tab_mf:
        st.markdown("### Συναρτήσεις συμμετοχής")
        st.write("Τριγωνικές και τραπεζοειδείς συναρτήσεις συμμετοχής για τις μεταβλητές εισόδου και εξόδου:")

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
        st.markdown("### Βάση ασαφών κανόνων (Mamdani FIS)")
        st.write(f"Ορίζονται {len(recommender.fuzzy_engine.rules)} κανόνες εμπειρογνώμονα (IF-THEN) για τον προσδιορισμό καταλληλότητας ανά τύπο προορισμού:")

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

        st.markdown("#### Μέθοδος αποσαφοποίησης (Κέντρο Βάρους / Centroid)")
        st.latex(r"z^* = \frac{\int z \cdot \mu_A(z) \, dz}{\int \mu_A(z) \, dz} \approx \frac{\sum_{i=1}^n z_i \cdot \mu_A(z_i)}{\sum_{i=1}^n \mu_A(z_i)}")
        st.info("Υπολογισμός κέντρου βάρους του συνενωμένου ασαφούς συνόλου εξόδου. Σε περίπτωση μηδενικής ενεργοποίησης κανόνα, αποδίδεται τιμή βάσης 10.0%.")

    with tab_fcm:
        st.markdown("### Μαθηματικό μοντέλο Fuzzy C-Means (FCM)")
        st.info("Σύνολο δεδομένων εκπαίδευσης: 350 συνθετικά δείγματα ταξιδιωτών σε 7 διαστάσεις χαρακτηριστικών.")
        st.latex(r"J_m = \sum_{i=1}^N \sum_{j=1}^C (u_{ij})^m \cdot \|x_i - v_j\|^2")
        st.markdown(r"""
        * $N = 350$ δείγματα εκπαίδευσης
        * $C = 5$ συστάδες (τουριστικά προφίλ)
        * $m = 2.0$ συντελεστής ασάφειας (fuzzifier)
        * $u_{ij} \in [0, 1]$ βαθμός συμμετοχής με $\sum_{j=1}^C u_{ij} = 1$
        * $v_j$ κεντροειδή συστάδων (ευθυγράμμιση Hungarian)
        """)

        metrics = recommender.fcm_model.compute_validation_metrics()
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Partition Coefficient (PC)", f"{metrics.get('partition_coefficient_PC', 0.0):.4f}", help="Μέτρο ευκρίνειας των συστάδων (1/C <= PC <= 1)")
        with col_m2:
            st.metric("Partition Entropy (PE)", f"{metrics.get('partition_entropy_PE', 0.0):.4f}", help="Μέτρο εντροπίας διαμέρισης (0 <= PE <= ln(C))")
        with col_m3:
            st.metric("Επαναλήψεις σύγκλισης", metrics.get("iterations_to_converge", 0))

        st.markdown("#### Κεντροειδή συστάδων σε φυσικές μονάδες")
        df_centroids = recommender.fcm_model.get_centroids_dataframe()
        st.dataframe(df_centroids, width="stretch")

        fig_cost = px.line(
            x=list(range(1, len(recommender.fcm_model.cost_history) + 1)),
            y=recommender.fcm_model.cost_history,
            labels={"x": "Επανάληψη", "y": "Συνάρτηση J_m"},
            title="Καμπύλη σύγκλισης FCM (J_m)"
        )
        fig_cost.update_layout(template="plotly_white", height=320)
        st.plotly_chart(fig_cost, use_container_width=True)

    with tab_feedback:
        st.markdown("### Μηχανισμός ανάδρασης (Feedback Loop)")
        st.write("Προσαρμογή τελικής βαθμολογίας βάσει καταγεγραμμένων αξιολογήσεων:")
        
        st.latex(r"\Delta_{\text{feedback}} = w_r \cdot (\bar{r} - 3.0) + w_a \cdot (\text{acceptance\_rate} - 0.5)")
        st.markdown(r"""
        Όπου $\bar{r}$ είναι ο μέσος όρος βαθμολογίας (1-5) και $\text{acceptance\_rate}$ το ποσοστό επιλογής. Προορισμοί με συνεπή θετική ανάδραση λαμβάνουν προσαρμογή έως +10%, ενώ απορριφθείσες επιλογές υποβαθμίζονται αυτόματα.
        """)

        fb_summary = recommender.feedback_mgr.get_overall_summary()
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            st.metric("Αξιολογήσεις", fb_summary["total_feedbacks"])
        with col_f2:
            st.metric("Μέση βαθμολογία", f"{fb_summary['avg_rating']}/5" if fb_summary["total_feedbacks"] > 0 else "N/A")
        with col_f3:
            st.metric("Ποσοστό αποδοχής", f"{fb_summary['acceptance_rate']}%" if fb_summary["total_feedbacks"] > 0 else "N/A")

        st.markdown("#### Ιστορικό καταγεγραμμένης ανάδρασης")
        all_fb = recommender.feedback_mgr.feedback_entries
        if all_fb:
            df_fb = pd.DataFrame([
                {
                    "Ημερομηνία": e["timestamp"][:19].replace("T", " "),
                    "Προορισμός": e["destination_name"],
                    "Βαθμολογία": f"{e['rating']}/5",
                    "Απόφαση": "Αποδοχή" if e["accepted"] else "Απόρριψη",
                    "Σχόλιο": e.get("comment", ""),
                    "Budget Χρήστη": f"{int(e['user_query'].get('budget', 0))}€",
                    "Θερμοκρασία": f"{int(e['user_query'].get('climate', 0))}°C"
                }
                for e in reversed(all_fb)
            ])
            st.dataframe(df_fb, width="stretch")
        else:
            st.info("Δεν υπάρχουν ακόμη καταγεγραμμένες αξιολογήσεις.")

# ==============================================================================
# MODE 3: INVENTORY & CATALOG MANAGEMENT
# ==============================================================================
elif app_mode == MODE_INVENTORY:
    st.markdown('<div class="main-title">Διαχείριση καταλόγου προορισμών</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Προβολή αποθέματος, προσθήκη νέων προορισμών και εξαγωγή δεδομένων σε CSV.</div>', unsafe_allow_html=True)

    df_cat = catalog_mgr.to_dataframe()
    st.dataframe(df_cat, width="stretch", height=350)

    csv_bytes = df_cat.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "Εξαγωγή καταλόγου σε CSV",
        data=csv_bytes,
        file_name="travel_catalog_inventory.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("Προσθήκη νέου προορισμού")

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

        new_desc = st.text_area("Περιγραφή", "Μεσαιωνική πόλη Ιπποτών, παραλίες και resorts.")
        new_pkg = st.text_input("Τίτλος Πακέτου", "Rhodes Knights & Coast (6D/5N)")
        new_img = st.text_input("URL Εικόνας", "https://images.unsplash.com/photo-1594918731553-73138b725c48?auto=format&fit=crop&w=800&q=80")

        save_btn = st.form_submit_button("Αποθήκευση στον κατάλογο", type="primary")

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
            st.success(f"Ο προορισμός '{new_name}' προστέθηκε επιτυχώς στη βάση δεδομένων.")
            st.rerun()
