"""Claymorphism visual theme: CSS injection and Plotly styling."""
import streamlit as st

INK = "#383139"
INK_SECONDARY = "#48404b"
ACCENT = "#f6a3ca"
GROUND = "#f1f2fa"
SURFACE = "#fffdf7"
SUPPORT = "#c0efdc"
COMPARE = "#ded0f9"
WARM = "#f9e7a8"
COOL = "#c5e5fb"

CLAY_SCALE = [[0.0, SUPPORT], [0.5, WARM], [1.0, ACCENT]]
CLAY_COLORWAY = ["#e0629f", "#6a52b8", "#2f9c78", "#d9a514", "#3a8fcf", INK_SECONDARY]
LINE_COLOR = "#e0629f"

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&display=swap');
@font-face {
  font-family: "Claymorphism Instrument";
  src: local("Instrument Sans");
}
:root {
  --dp-color-ground: #f1f2fa; --dp-color-ink: #383139; --dp-color-ink-secondary: #48404b;
  --dp-color-accent: #f6a3ca; --dp-color-surface-support: #c0efdc;
  --dp-color-surface-compare: #ded0f9; --dp-color-surface-warm: #f9e7a8;
  --dp-color-surface-cool: #c5e5fb; --dp-color-surface: #fffdf7;
  --dp-typography-face: "Claymorphism Instrument", "Instrument Sans", sans-serif;
  --dp-spacing-gap: 24px; --dp-spacing-gap-compact: 20px;
  --dp-radius-surface: 38px; --dp-radius-tray: 70px; --dp-radius-control: 999px;
  --dp-radius-disclosure: 25px; --dp-border-focus-width: 3px; --dp-motion-interaction: 180ms;
  --clay-outer: 0 22px 40px rgba(120, 100, 150, .20);
  --clay-outer-small: 0 10px 20px rgba(120, 100, 150, .20);
  --clay-inset: inset 6px 6px 12px rgba(255, 255, 255, .85), inset -8px -8px 16px rgba(120, 90, 140, .16);
}
html, body, .stApp, [class*="st-"], button, input, textarea, select {
  font-family: var(--dp-typography-face);
}
.stApp { background: var(--dp-color-ground); color: var(--dp-color-ink); }
.stApp [data-testid="stIconMaterial"], .stApp span[class*="material"] {
  font-family: "Material Symbols Rounded", "Material Icons" !important;
}
h1, h2, h3, h4 { color: var(--dp-color-ink); font-weight: 700; letter-spacing: -0.02em; line-height: 1.15; }
p, li, label, .stMarkdown, [data-testid="stCaptionContainer"] { color: var(--dp-color-ink-secondary); line-height: 1.55; }

/* Shared cream tray holds each tab's content */
[data-baseweb="tab-panel"] {
  background: var(--dp-color-surface);
  border-radius: var(--dp-radius-tray);
  box-shadow: var(--clay-outer), var(--clay-inset);
  padding: 2.5rem clamp(1.25rem, 4vw, 3.5rem) 2.5rem;
  margin-top: var(--dp-spacing-gap);
}
[data-baseweb="tab-list"] { gap: 12px; padding: 6px 4px 10px; background: transparent; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none; }
button[data-baseweb="tab"] {
  background: var(--dp-color-surface-cool); border-radius: var(--dp-radius-control);
  padding: 10px 22px; height: auto; color: var(--dp-color-ink); font-weight: 700;
  box-shadow: var(--clay-outer-small), var(--clay-inset);
  transition: transform var(--dp-motion-interaction), box-shadow var(--dp-motion-interaction);
}
button[data-baseweb="tab"][aria-selected="true"] { background: var(--dp-color-accent); }
button[data-baseweb="tab"]:hover { transform: translateY(-2px); }
button[data-baseweb="tab"] p { color: var(--dp-color-ink); font-weight: 700; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--dp-color-surface-compare);
  border-radius: 0 var(--dp-radius-surface) var(--dp-radius-surface) 0;
  box-shadow: var(--clay-outer), var(--clay-inset);
}
[data-testid="stSidebar"] * { color: var(--dp-color-ink); }

/* Metrics become pastel cushions */
[data-testid="stMetric"] {
  background: var(--dp-color-surface-support); border-radius: var(--dp-radius-surface);
  padding: 22px 26px; box-shadow: var(--clay-outer-small), var(--clay-inset);
}
[data-testid="column"]:nth-child(2) [data-testid="stMetric"] { background: var(--dp-color-surface-warm); }
[data-testid="column"]:nth-child(3) [data-testid="stMetric"] { background: var(--dp-color-surface-cool); }
[data-testid="stMetricLabel"] p { color: var(--dp-color-ink); font-weight: 600; }
[data-testid="stMetricValue"] { color: var(--dp-color-ink); font-weight: 700; letter-spacing: -0.02em; }

/* Buttons: thick pills */
.stButton > button, .stDownloadButton > button {
  background: var(--dp-color-accent); color: var(--dp-color-ink); font-weight: 700;
  border: 0; border-radius: var(--dp-radius-control); padding: 10px 24px;
  box-shadow: 0 10px 18px rgba(120, 100, 150, .25), var(--clay-inset);
  transition: transform var(--dp-motion-interaction), box-shadow var(--dp-motion-interaction);
}
.stButton > button:hover { transform: translateY(-2px); color: var(--dp-color-ink); }
.stButton > button:active { transform: translateY(1px) scale(.98);
  box-shadow: 0 4px 8px rgba(120, 100, 150, .2), inset 4px 4px 10px rgba(120, 90, 140, .25); }

/* Inputs: recessed wells */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="base-input"] {
  background: var(--dp-color-ground) !important; border-radius: var(--dp-radius-disclosure) !important;
  border-color: transparent !important;
  box-shadow: inset 4px 4px 9px rgba(120, 90, 140, .16), inset -4px -4px 9px rgba(255, 255, 255, .9);
}
input { color: var(--dp-color-ink) !important; }
[data-baseweb="tag"] { background: var(--dp-color-surface-compare) !important; border-radius: var(--dp-radius-control) !important; }
[data-baseweb="tag"] span { color: var(--dp-color-ink) !important; }

/* Disclosures and tables */
[data-testid="stExpander"] details {
  background: var(--dp-color-surface-warm); border: 0; border-radius: var(--dp-radius-disclosure);
  box-shadow: var(--clay-outer-small), var(--clay-inset);
}
[data-testid="stExpander"] summary { font-weight: 700; color: var(--dp-color-ink); }
[data-testid="stAlert"] { border-radius: var(--dp-radius-disclosure); color: var(--dp-color-ink); box-shadow: var(--clay-inset); }
[data-testid="stDataFrame"] { border-radius: var(--dp-radius-disclosure); overflow: hidden;
  box-shadow: var(--clay-outer-small), var(--clay-inset); }
[data-testid="stPlotlyChart"] { background: var(--dp-color-surface); border-radius: var(--dp-radius-surface);
  padding: 12px; box-shadow: var(--clay-outer-small), var(--clay-inset); overflow: hidden; }
hr { border-color: rgba(120, 90, 140, .15); }

/* Visible focus, separate from shading */
:is(button, input, select, textarea, summary, [role="tab"], [tabindex]):focus-visible {
  outline: var(--dp-border-focus-width) solid var(--dp-color-ink) !important; outline-offset: 3px;
}

@media (max-width: 1100px) { [data-baseweb="tab-panel"] { border-radius: 50px; } }
@media (max-width: 760px) {
  [data-baseweb="tab-panel"] { border-radius: var(--dp-radius-surface); padding: 1.5rem 1rem; }
  [data-testid="stMetric"] { padding: 16px 18px; }
}
@media (max-width: 460px) { [data-baseweb="tab-panel"] { border-radius: 28px; } }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; animation: none !important; }
  .stButton > button:hover, button[data-baseweb="tab"]:hover { transform: none; }
}
"""


def apply_theme() -> None:
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


def style_figure(fig):
    """Apply clay colors and typography to a Plotly figure."""
    fig.update_layout(
        font=dict(family="Instrument Sans, sans-serif", color=INK),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        colorway=CLAY_COLORWAY,
        title_font=dict(size=18, color=INK),
    )
    fig.update_xaxes(gridcolor="rgba(120,90,140,.15)", zerolinecolor="rgba(120,90,140,.25)")
    fig.update_yaxes(gridcolor="rgba(120,90,140,.15)", zerolinecolor="rgba(120,90,140,.25)")
    return fig
