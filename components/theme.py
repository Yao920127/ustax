"""Industrial visual theme: CSS injection and Plotly styling."""
import streamlit as st

CHASSIS = "#cbd0d2"
RAISED = "#e7eaeb"
WELL = "#b6bec2"
INK = "#181e22"
LABEL = "#414b52"
FIELD = "#20272b"
ON_FIELD = "#f2f4f4"
ACCENT = "#f15b22"

SCALE = [[0.0, "#e7eaeb"], [0.5, "#8a959b"], [1.0, ACCENT]]
COLORWAY = [ACCENT, "#20272b", "#5f6b72", "#9aa4a9", "#b5431a", "#414b52"]
LINE_COLOR = ACCENT

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Host+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
@font-face { font-family: "Industrial Host"; src: local("Host Grotesk"); }
@font-face { font-family: "Industrial Plex"; src: local("IBM Plex Mono"); }
:root {
  --dp-color-chassis: #cbd0d2; --dp-color-raised: #e7eaeb; --dp-color-well: #b6bec2;
  --dp-color-ink: #181e22; --dp-color-label: #414b52; --dp-color-field: #20272b;
  --dp-color-on-field: #f2f4f4; --dp-color-accent: #f15b22;
  --dp-typography-sans: "Industrial Host", "Host Grotesk", sans-serif;
  --dp-typography-mono: "Industrial Plex", "IBM Plex Mono", monospace;
  --dp-radius-key: 4px; --dp-motion-key: 140ms; --dp-motion-settle: cubic-bezier(0.3, 0.7, 0.4, 1.25);
  --raised-shadow: inset 1px 1px 0 rgba(255,255,255,.9), inset -1px -1px 0 rgba(0,0,0,.18), 3px 4px 8px rgba(24,30,34,.22);
  --recess-shadow: inset 3px 3px 6px rgba(24,30,34,.25), inset -2px -2px 4px rgba(255,255,255,.55);
}
html, body, .stApp, [class*="st-"], button, input, textarea, select { font-family: var(--dp-typography-sans); }
.stApp [data-testid="stIconMaterial"], .stApp span[class*="material"] {
  font-family: "Material Symbols Rounded", "Material Icons" !important;
}
.stApp { background: linear-gradient(160deg, #d6dadc, var(--dp-color-chassis)); color: var(--dp-color-ink); }
h1, h2, h3, h4 { color: var(--dp-color-ink); font-weight: 700; letter-spacing: -0.025em; line-height: 1.1; }
p, li, label, .stMarkdown { color: var(--dp-color-ink); line-height: 1.55; }
[data-testid="stCaptionContainer"], label p { color: var(--dp-color-label); }
label p, [data-testid="stMetricLabel"] p, [data-baseweb="tab"] p {
  font-family: var(--dp-typography-mono); font-size: 12px; letter-spacing: .06em; text-transform: uppercase;
}

/* Housing: broad rounded case with a vertical seam */
.block-container {
  background: var(--dp-color-chassis); border-radius: 18px; margin-top: 1rem; margin-bottom: 1rem;
  padding: 2.5rem clamp(1rem, 4vw, 3.5rem) !important;
  box-shadow: var(--raised-shadow), 0 24px 48px rgba(24,30,34,.25);
  background-image: linear-gradient(90deg, transparent calc(100% - 14px), rgba(24,30,34,.18) calc(100% - 14px), rgba(24,30,34,.18) calc(100% - 13px), rgba(255,255,255,.6) calc(100% - 13px), transparent calc(100% - 12px));
}

/* Navigation: bank of raised keys */
[data-baseweb="tab-list"] { gap: 8px; background: transparent; padding-bottom: 8px; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none; }
button[data-baseweb="tab"] {
  background: var(--dp-color-raised); border-radius: var(--dp-radius-key); height: auto; padding: 10px 18px;
  box-shadow: var(--raised-shadow);
  transition: transform 130ms var(--dp-motion-settle), box-shadow 130ms var(--dp-motion-settle);
}
button[data-baseweb="tab"]:hover { transform: translateY(-1px); }
button[data-baseweb="tab"][aria-selected="true"] {
  background: var(--dp-color-well); box-shadow: var(--recess-shadow); border-bottom: 3px solid var(--dp-color-accent);
}
button[data-baseweb="tab"] p { color: var(--dp-color-ink); font-weight: 500; }
[data-baseweb="tab-panel"] {
  background: var(--dp-color-raised); border-radius: var(--dp-radius-key); margin-top: 12px;
  padding: 2rem clamp(1rem, 3vw, 2.5rem); box-shadow: var(--raised-shadow);
}

/* Sidebar */
[data-testid="stSidebar"] { background: var(--dp-color-well); box-shadow: inset -2px 0 0 rgba(24,30,34,.2), inset -3px 0 0 rgba(255,255,255,.5); }
[data-testid="stSidebar"] * { color: var(--dp-color-ink); }

/* Metrics: recessed dark screens with orange lamp */
[data-testid="stMetric"] {
  background: var(--dp-color-field); border-radius: var(--dp-radius-key); padding: 18px 22px;
  box-shadow: inset 3px 3px 8px rgba(0,0,0,.6), inset -1px -1px 0 rgba(255,255,255,.12), 0 1px 0 rgba(255,255,255,.8);
  border-left: 4px solid var(--dp-color-accent);
}
[data-testid="stMetricLabel"] p { color: #d8dee1; }
[data-testid="stMetricValue"] { color: var(--dp-color-on-field); font-weight: 700; letter-spacing: -0.02em; }

/* Buttons: rectangular raised keys */
.stButton > button, .stDownloadButton > button {
  background: var(--dp-color-raised); color: var(--dp-color-ink); font-weight: 600;
  border: 0; border-radius: var(--dp-radius-key); padding: 8px 20px; box-shadow: var(--raised-shadow);
  transition: transform var(--dp-motion-key) var(--dp-motion-settle), box-shadow var(--dp-motion-key) var(--dp-motion-settle);
}
.stButton > button:hover { transform: translateY(-1px); color: var(--dp-color-ink); }
.stButton > button:active { transform: translateY(1px); box-shadow: var(--recess-shadow); }

/* Inputs: recessed wells */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="base-input"] {
  background: var(--dp-color-well) !important; border-radius: var(--dp-radius-key) !important;
  border-color: transparent !important; box-shadow: var(--recess-shadow);
}
input { color: var(--dp-color-ink) !important; font-family: var(--dp-typography-mono); }
[data-baseweb="tag"] { background: var(--dp-color-field) !important; border-radius: var(--dp-radius-key) !important; }
[data-baseweb="tag"] span { color: var(--dp-color-on-field) !important; }

/* Disclosures, alerts, data */
[data-testid="stExpander"] details { background: var(--dp-color-raised); border: 0; border-radius: var(--dp-radius-key); box-shadow: var(--raised-shadow); }
[data-testid="stExpander"] summary { font-weight: 600; }
[data-testid="stAlert"] { border-radius: var(--dp-radius-key); color: var(--dp-color-ink); box-shadow: var(--recess-shadow); }
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {
  border-radius: var(--dp-radius-key); box-shadow: var(--recess-shadow); overflow: hidden; background: var(--dp-color-raised);
}
[data-testid="stPlotlyChart"] { padding: 8px; }
hr { border-color: rgba(24,30,34,.2); }

/* Focus sits outside the physical edge */
:is(button, input, select, textarea, summary, [role="tab"], [tabindex]):focus-visible {
  outline: 3px solid var(--dp-color-accent) !important; outline-offset: 3px;
}

@media (max-width: 760px) { .block-container { border-radius: 12px; padding: 1.25rem .75rem !important; } }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; animation: none !important; }
  .stButton > button:hover, .stButton > button:active, button[data-baseweb="tab"]:hover { transform: none; }
}
"""


def apply_theme() -> None:
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


def style_figure(fig):
    """Apply industrial colors and typography to a Plotly figure."""
    fig.update_layout(
        font=dict(family="IBM Plex Mono, monospace", color=INK, size=12),
        paper_bgcolor=RAISED,
        plot_bgcolor=RAISED,
        colorway=COLORWAY,
        title_font=dict(family="Host Grotesk, sans-serif", size=18, color=INK),
    )
    fig.update_xaxes(gridcolor="rgba(24,30,34,.15)", zerolinecolor="rgba(24,30,34,.3)")
    fig.update_yaxes(gridcolor="rgba(24,30,34,.15)", zerolinecolor="rgba(24,30,34,.3)")
    return fig
