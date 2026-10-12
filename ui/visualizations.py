"""
Visualization helpers for the Tourism Fuzzy Recommender.
Generates interactive Plotly and Matplotlib charts for:
- Fuzzy Membership Functions (Universes of Discourse)
- FCM Persona Spider / Radar Charts
- Destination Multi-Criteria Score Breakdowns
- Active Fuzzy Rules Firing Strength
- Defuzzification Output Surface
"""
from typing import Dict, List, Any, Optional
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from core.membership import LinguisticVariable


def plot_fuzzy_variable(var: LinguisticVariable, current_value: Optional[float] = None) -> go.Figure:
    """Generates an interactive Plotly figure displaying all membership functions of a linguistic variable."""
    u_min, u_max = var.universe
    x = np.linspace(u_min, u_max, 400)

    fig = go.Figure()

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    for idx, (term, fset) in enumerate(var.sets.items()):
        y = fset.membership(x)
        color = colors[idx % len(colors)]
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            name=f"{term}",
            line=dict(width=2.5, color=color),
            fill='tozeroy',
            fillcolor=f"rgba{tuple(list(bytes.fromhex(color.lstrip('#')))+[0.15])}"
        ))

    if current_value is not None:
        fig.add_vline(
            x=current_value,
            line_width=2.5,
            line_dash="dash",
            line_color="#e74c3c",
            annotation_text=f"Είσοδος: {current_value} {var.unit}",
            annotation_position="top right"
        )

    fig.update_layout(
        title=f"Συναρτήσεις Συμμετοχής: {var.name.capitalize()} [{var.unit}]",
        xaxis_title=f"{var.name.capitalize()} ({var.unit})",
        yaxis_title="Βαθμός Συμμετοχής μ(x)",
        yaxis=dict(range=[-0.05, 1.05]),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        height=320
    )
    return fig


def plot_persona_radar_chart(persona_results: List[Dict[str, Any]]) -> go.Figure:
    """Generates a Radar (Spider) chart showing FCM soft membership across tourist personas."""
    categories = [p["greek_name"] for p in persona_results]
    values = [p["membership_pct"] for p in persona_results]

    # Close the radar polygon
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(46, 204, 113, 0.25)',
        line=dict(color='#27ae60', width=2.5),
        name='Προφίλ Ταξιδιώτη'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max(values) + 10, 50)]
            )
        ),
        showlegend=False,
        title="FCM Soft Persona Distribution (% Συμμετοχή)",
        template="plotly_white",
        height=380,
        margin=dict(l=40, r=40, t=45, b=30)
    )
    return fig


def plot_destination_scores_breakdown(component_scores: Dict[str, float], dest_name: str) -> go.Figure:
    """Generates a horizontal bar chart displaying component criteria scores for a destination."""
    labels = [
        "Fuzzy Archetype",
        "Budget Match",
        "Activity Fit",
        "Climate Match",
        "Duration Fit"
    ]
    keys = [
        "archetype_fuzzy",
        "budget_compatibility",
        "activity_alignment",
        "climate_match",
        "duration_fit"
    ]
    vals = [component_scores.get(k, 0.0) for k in keys]

    # Color grading based on score
    colors = ['#2ecc71' if v >= 75 else '#f39c12' if v >= 50 else '#e74c3c' for v in vals]

    fig = go.Figure(go.Bar(
        x=vals,
        y=labels,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{v:.1f}%" for v in vals],
        textposition='auto'
    ))

    fig.update_layout(
        title=f"Ανάλυση Κριτηρίων: {dest_name}",
        xaxis=dict(range=[0, 105], title="Βαθμός Συμβατότητας (%)"),
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
        height=260,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def plot_active_rules_chart(active_rules: List[Dict[str, Any]]) -> go.Figure:
    """Generates a bar chart displaying active fuzzy rules and their firing strengths (alpha-cuts)."""
    if not active_rules:
        fig = go.Figure()
        fig.add_annotation(text="Δεν ενεργοποιήθηκαν κανόνες", showarrow=False)
        return fig

    rule_labels = [f"{r['rule_id']}: {r['archetype'][:16]}..." for r in active_rules]
    strengths = [r["strength"] for r in active_rules]

    fig = go.Figure(go.Bar(
        x=strengths,
        y=rule_labels,
        orientation='h',
        marker=dict(color='#3498db'),
        text=[f"α = {s:.3f}" for s in strengths],
        textposition='auto'
    ))

    fig.update_layout(
        title="Ενεργοποιημένοι Ασαφείς Κανόνες (Firing Strength α)",
        xaxis=dict(range=[0, 1.05], title="Firing Strength (Min Antecedent)"),
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
        height=280,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
