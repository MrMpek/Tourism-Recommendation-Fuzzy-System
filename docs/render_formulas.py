"""
Renders mathematical formulas as high-resolution PNG images using Matplotlib mathtext.
Formulas are saved in docs/figures/formulas/ and inserted into academic reports (DOCX & PDF).
"""
import os
import tempfile

# Prevent matplotlib from trying to write to read-only home directories
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_fuzzy_cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image


FORMULAS = {
    "formula_centroid.png": (
        r"$z^* = \frac{\int z \cdot \mu_A(z) \, dz}{\int \mu_A(z) \, dz} \approx \frac{\sum_{i=1}^n z_i \cdot \mu_A(z_i)}{\sum_{i=1}^n \mu_A(z_i)}$",
        "z* = [ ∫ z · μ_A(z) dz ] / [ ∫ μ_A(z) dz ] ≈ [ Σ (z_i · μ_A(z_i)) ] / [ Σ μ_A(z_i) ]"
    ),
    "formula_fcm_cost.png": (
        r"$J_m = \sum_{i=1}^N \sum_{j=1}^C (u_{ij})^m \cdot \|x_i - v_j\|^2$",
        "J_m = Σ(i=1..N) Σ(j=1..C) u_ij^m · ‖x_i − v_j‖²"
    ),
    "formula_persona_affinity.png": (
        r"$\mathrm{persona\_affinity}(\mathrm{archetype}) = \sum_{j=1}^{5} u_j \cdot W_{j, \mathrm{archetype}}$",
        "persona_affinity(archetype) = Σ(j=1..5) [ u_j · W[j][archetype] ]"
    ),
    "formula_basescore.png": (
        r"$\mathrm{BaseScore} = 0.25 \cdot S_{\mathrm{arch}} + 0.15 \cdot S_{\mathrm{persona}} + 0.20 \cdot S_{\mathrm{budget}} + 0.20 \cdot S_{\mathrm{activity}} + 0.10 \cdot S_{\mathrm{climate}} + 0.10 \cdot S_{\mathrm{duration}}$",
        "BaseScore = 0.25·ArchScore + 0.15·PersonaScore + 0.20·BudgetScore + 0.20·ActivityScore + 0.10·ClimateScore + 0.10·DurationScore"
    ),
    "formula_finalscore.png": (
        r"$\mathrm{FinalScore} = \mathrm{BaseScore} + \Delta_{\mathrm{feedback}}$",
        "FinalScore = BaseScore + Δ_feedback"
    ),
    "formula_feedback_delta.png": (
        r"$\Delta_{\mathrm{feedback}} = w_r \cdot (\bar{r} - 3.0) + w_a \cdot (\mathrm{AcceptanceRate} - 0.5)$",
        "Δ_feedback = w_r · ( r̄ − 3.0 ) + w_a · ( AcceptanceRate − 0.5 )"
    )
}


def render_all_formulas(output_dir: str = None) -> dict:
    """
    Renders all mathematical formula images.
    Returns dict mapping formula key to { 'path': filepath, 'fallback': text, 'size': (w, h) }
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", "formulas")
    os.makedirs(output_dir, exist_ok=True)

    rendered = {}
    for filename, (latex_code, fallback_txt) in FORMULAS.items():
        out_path = os.path.join(output_dir, filename)
        # Render if not exists or empty
        if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            fig = plt.figure(figsize=(7, 0.8), dpi=300)
            fig.text(
                0.5, 0.5, latex_code,
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=12,
                color="#0c2461"
            )
            plt.savefig(out_path, bbox_inches="tight", pad_inches=0.06, transparent=True)
            plt.close(fig)

        # Get dimensions
        try:
            with Image.open(out_path) as im:
                size = im.size
        except Exception:
            size = (600, 100)

        rendered[filename] = {
            "path": out_path,
            "fallback": fallback_txt,
            "size": size
        }

    return rendered


if __name__ == "__main__":
    res = render_all_formulas()
    for k, v in res.items():
        print(f"{k}: {v['size']}, path={v['path']}")
