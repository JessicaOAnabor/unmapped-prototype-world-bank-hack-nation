
# UNMAPPED — PROTOTYPE BY JESSICA ANABOR FOR WORLD BANK HACK NATION HACKATHON




import os
import re
from functools import lru_cache

import numpy as np
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px
import gradio as gr

# ============================================================
# STYLE
# ============================================================

CSS = """
/* Overall */
.gradio-container {
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

/* Force readable inputs (fix for dark textboxes / black-on-black) */
.gradio-container input,
.gradio-container textarea,
.gradio-container select {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #cbd5e1 !important;
    caret-color: #111827 !important;
}

.gradio-container input::placeholder,
.gradio-container textarea::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

.gradio-container input:focus,
.gradio-container textarea:focus,
.gradio-container select:focus {
    border-color: #10b981 !important;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.14) !important;
}

/* Headings */
#hero {
    text-align: center;
    padding: 8px 0 4px 0;
}
#hero h1 {
    font-size: 48px;
    line-height: 1.05;
    margin: 0;
    font-weight: 900;
    letter-spacing: -0.04em;
}
#hero p {
    margin: 10px auto 0 auto;
    max-width: 980px;
    font-size: 15px;
    line-height: 1.55;
    color: #334155;
}

/* Cards */
.card {
    border: 1px solid #e2e8f0;
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 18px;
    padding: 16px 16px 14px 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

.card-dark {
    border: 1px solid rgba(148,163,184,0.22);
    background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
    color: #e5e7eb;
    border-radius: 18px;
    padding: 16px 16px 14px 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.14);
}

.kpi {
    display: inline-block;
    min-width: 170px;
    margin: 6px 10px 6px 0;
    padding: 12px 14px;
    border-radius: 16px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 6px 18px rgba(15,23,42,0.05);
}
.kpi .label {
    font-size: 12px;
    color: #64748b;
    margin-bottom: 2px;
}
.kpi .value {
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
}
.kpi .sub {
    font-size: 12px;
    color: #475569;
    margin-top: 2px;
}

.badge {
    display:inline-block;
    padding: 5px 10px;
    margin: 0 6px 6px 0;
    border-radius: 999px;
    font-size: 12px;
    border: 1px solid #cbd5e1;
    background: #f8fafc;
    color: #0f172a;
}

.callout {
    border-left: 4px solid #10b981;
    background: rgba(16,185,129,0.08);
    padding: 10px 12px;
    border-radius: 12px;
    margin-top: 10px;
    color: #0f172a;
}

.warn {
    border-left: 4px solid #f59e0b;
    background: rgba(245,158,11,0.10);
    padding: 10px 12px;
    border-radius: 12px;
    margin-top: 10px;
    color: #0f172a;
}

.mono {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    font-size: 12px;
    color: #334155;
}

.small {
    font-size: 12px;
    color: #64748b;
    line-height: 1.5;
}

.section-title {
    font-size: 18px;
    font-weight: 800;
    margin: 0 0 8px 0;
    color: #0f172a;
}

hr.soft {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 14px 0;
}
"""


# COUNTRY PACKS / LOCALIZABLE CONFIG


COUNTRY_PACKS = {
    "ghana_urban": {
        "country_code": "GHA",
        "country_name": "Ghana",
        "context_name": "Sub-Saharan Africa | urban informal economy",
        "ui_language": "English",
        "script": "Latin",
        "education_taxonomy": "Secondary certificate + informal skill recognition",
        "automation_calibration": 0.86,
        "opportunity_types": ["self_employment", "formal_employment", "gig_work", "training"],
        "constraint": "shared devices, uneven broadband, informal matching channels",
        "tag": "Ghana / urban informal"
    },
    "india_rural": {
        "country_code": "IND",
        "country_name": "India",
        "context_name": "South Asia | rural agricultural transition",
        "ui_language": "English",
        "script": "Latin",
        "education_taxonomy": "School certificate + vocational / apprenticeship pathways",
        "automation_calibration": 0.74,
        "opportunity_types": ["self_employment", "farm_value_chain", "formal_employment", "training"],
        "constraint": "low bandwidth, seasonal work, mobile-first access",
        "tag": "India / rural agricultural"
    }
}

SWAP_CONTEXT = {
    "ghana_urban": "india_rural",
    "india_rural": "ghana_urban"
}

# Real public labour signals from World Bank API
WDI_INDICATORS = {
    "Youth NEET (%)": "SL.UEM.NEET.ZS",
    "Employment to population ratio, 15+ (%)": "SL.EMP.TOTL.SP.ZS",
    "Vulnerable employment (% total employment)": "SL.EMP.VULN.ZS",
    "Internet users (% population)": "IT.NET.USER.ZS",
    "GDP per capita (current US$)": "NY.GDP.PCAP.CD",
    "Secondary school enrollment (%)": "SE.SEC.ENRR",
}

# Starter occupation graph; replaceable with ESCO / O*NET / ISCO expansion later
OCCUPATIONS = [
    {
        "occupation": "Electronics / phone repair technician",
        "taxonomy_family": "ISCO/ESCO-aligned technical services",
        "exposure": 0.38,
        "routine": 0.45,
        "manual": 0.72,
        "cognitive": 0.42,
        "keywords": ["repair", "phone", "electronics", "screen", "battery", "solder", "diagnose"],
        "durable_skills": ["problem solving", "manual dexterity", "customer communication", "diagnosis"],
        "adjacent_skills": ["inventory tracking", "basic bookkeeping", "warranty handling", "digital diagnostics"],
        "opportunities": ["repair microenterprise", "electronics apprenticeship", "refurbishment workshop", "field service technician"]
    },
    {
        "occupation": "Retail sales / market trader",
        "taxonomy_family": "ISCO/ESCO-aligned sales and service",
        "exposure": 0.53,
        "routine": 0.60,
        "manual": 0.38,
        "cognitive": 0.44,
        "keywords": ["sell", "sales", "market", "customer", "cash", "shop", "retail"],
        "durable_skills": ["customer service", "negotiation", "cash handling", "product knowledge"],
        "adjacent_skills": ["digital payments", "stock management", "merchandising", "marketing"],
        "opportunities": ["micro-retail", "sales associate", "mobile money agent", "market stall expansion"]
    },
    {
        "occupation": "Bookkeeping / admin assistant",
        "taxonomy_family": "ISCO/ESCO-aligned clerical services",
        "exposure": 0.71,
        "routine": 0.81,
        "manual": 0.18,
        "cognitive": 0.60,
        "keywords": ["bookkeeping", "accounts", "admin", "typing", "excel", "records", "receipt"],
        "durable_skills": ["attention to detail", "record keeping", "numeracy", "data entry"],
        "adjacent_skills": ["spreadsheet skills", "payroll basics", "digital filing", "procurement records"],
        "opportunities": ["assistant accountant", "office clerk", "digital records helper", "small business admin"]
    },
    {
        "occupation": "Tailor / seamstress",
        "taxonomy_family": "ISCO/ESCO-aligned craft and garment services",
        "exposure": 0.46,
        "routine": 0.47,
        "manual": 0.78,
        "cognitive": 0.31,
        "keywords": ["tailor", "sew", "sewing", "fashion", "dress", "alter", "garment"],
        "durable_skills": ["craft precision", "measurement", "design adaptation", "client preference handling"],
        "adjacent_skills": ["pattern making", "online sales", "pricing", "fabric sourcing"],
        "opportunities": ["garment microenterprise", "alterations service", "fashion apprenticeship", "uniform production"]
    },
    {
        "occupation": "Motorcycle / small engine mechanic",
        "taxonomy_family": "ISCO/ESCO-aligned mechanical trades",
        "exposure": 0.41,
        "routine": 0.39,
        "manual": 0.77,
        "cognitive": 0.43,
        "keywords": ["mechanic", "engine", "motorcycle", "repair", "bike", "garage", "vehicle"],
        "durable_skills": ["diagnosis", "tool handling", "maintenance", "repair sequencing"],
        "adjacent_skills": ["parts ordering", "service logs", "electrical troubleshooting", "customer estimates"],
        "opportunities": ["garage apprenticeship", "mobile repair service", "fleet maintenance", "parts dealership support"]
    },
    {
        "occupation": "Delivery rider / logistics runner",
        "taxonomy_family": "ISCO/ESCO-aligned transport and logistics",
        "exposure": 0.57,
        "routine": 0.63,
        "manual": 0.61,
        "cognitive": 0.34,
        "keywords": ["delivery", "rider", "logistics", "dispatch", "bike", "parcel", "route"],
        "durable_skills": ["route navigation", "time discipline", "customer handoff", "safety awareness"],
        "adjacent_skills": ["digital dispatch", "fleet apps", "service ratings", "basic maintenance"],
        "opportunities": ["gig delivery", "dispatch assistant", "courier services", "last-mile logistics"]
    },
    {
        "occupation": "Community health worker / caregiver",
        "taxonomy_family": "ISCO/ESCO-aligned health support services",
        "exposure": 0.24,
        "routine": 0.18,
        "manual": 0.51,
        "cognitive": 0.55,
        "keywords": ["health", "care", "community", "patient", "clinic", "support", "counsel"],
        "durable_skills": ["empathy", "communication", "trust building", "basic health guidance"],
        "adjacent_skills": ["record keeping", "referral pathways", "mobile health tools", "safeguarding"],
        "opportunities": ["community health aide", "care support", "clinic assistant", "outreach work"]
    },
    {
        "occupation": "Agricultural labour / farm helper",
        "taxonomy_family": "ISCO/ESCO-aligned primary sector work",
        "exposure": 0.33,
        "routine": 0.46,
        "manual": 0.81,
        "cognitive": 0.28,
        "keywords": ["farm", "agriculture", "crop", "harvest", "plant", "livestock", "field"],
        "durable_skills": ["seasonal planning", "animal care", "tool use", "crop handling"],
        "adjacent_skills": ["post-harvest handling", "aggregation", "market linkage", "irrigation basics"],
        "opportunities": ["farm enterprise", "agri-input sales", "aggregation work", "extension support"]
    }
]


# HELPERS


def clean_text(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def badge_list(items):
    return "".join([f"<span class='badge'>{x}</span>" for x in items])

def as_money(v):
    try:
        return f"${float(v):,.0f}"
    except Exception:
        return "Not available"

def as_percent(v):
    try:
        return f"{float(v):.1f}%"
    except Exception:
        return "Not available"

@lru_cache(maxsize=64)
def wb_latest(country_code: str, indicator: str):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&per_page=1000"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list) or len(data) < 2:
            return None, None
        for row in data[1]:
            if row and row.get("value") is not None:
                return row.get("value"), row.get("date")
    except Exception:
        pass
    return None, None

def fetch_wdi(country_code, country_name):
    rows = []
    for label, ind in WDI_INDICATORS.items():
        value, year = wb_latest(country_code, ind)
        rows.append({
            "signal": label,
            "value": value,
            "year": year if year else "latest",
            "source": "World Bank WDI API",
            "country": country_name
        })
    return pd.DataFrame(rows)

def normalize_for_chart(signal_name, value):
    if value is None or pd.isna(value):
        return 0
    if "GDP per capita" in signal_name:
        return min(max(float(value) / 120000 * 100, 0), 100)
    if "Secondary school" in signal_name:
        return min(max(float(value), 0), 100)
    return min(max(float(value), 0), 100)

def load_csv_if_present(path):
    if path and isinstance(path, str) and os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


# PROFILE / RISK / MATCHING LOGIC


SKILL_AXES = {
    "repair": ["repair", "fix", "electronics", "phone", "engine", "mechanic", "tool", "maintenance"],
    "sales": ["sell", "sales", "customer", "market", "shop", "retail", "cash", "merchandise"],
    "digital": ["excel", "computer", "typing", "coding", "data", "digital", "mobile", "internet", "software"],
    "care": ["care", "health", "support", "teach", "counsel", "community", "patient"],
    "craft": ["sew", "tailor", "fashion", "design", "craft", "measure", "garment"],
    "agri": ["farm", "agri", "crop", "livestock", "harvest", "irrigation", "field"],
    "logistics": ["delivery", "route", "logistics", "dispatch", "transport", "rider", "parcel"],
    "admin": ["record", "bookkeeping", "admin", "excel", "receipt", "file", "invoice", "account"],
}

def infer_axes(*texts):
    text = clean_text(" ".join([t or "" for t in texts]))
    scores = {}
    for axis, kws in SKILL_AXES.items():
        scores[axis] = sum(1 for k in kws if k in text)
    maxv = max(max(scores.values()), 1)
    for k in scores:
        scores[k] = round((scores[k] / maxv) * 5, 2)
    return scores

def score_occ(profile_text, occ):
    text = clean_text(profile_text)
    score = 0
    matched = []
    for kw in occ["keywords"]:
        if kw in text:
            score += 1
            matched.append(kw)
    for part in occ["occupation"].lower().replace("/", " ").split():
        if len(part) > 3 and part in text:
            score += 0.5
            matched.append(part)
    return score, matched

def best_occupation(profile_text):
    scored = []
    for occ in OCCUPATIONS:
        s, matched = score_occ(profile_text, occ)
        scored.append((s, occ, matched))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[0]
    if top[0] <= 0:
        top = (0, OCCUPATIONS[0], [])
    return top, scored

def portability_score(axis_scores):
    score = (
        axis_scores.get("digital", 0) * 1.2 +
        axis_scores.get("admin", 0) * 1.0 +
        axis_scores.get("sales", 0) * 1.0 +
        axis_scores.get("care", 0) * 1.0 +
        axis_scores.get("repair", 0) * 0.9 +
        axis_scores.get("craft", 0) * 0.9 +
        axis_scores.get("agri", 0) * 0.8 +
        axis_scores.get("logistics", 0) * 0.9
    )
    return round(min(score / 8 * 100, 100), 1)

def risk_band(score):
    if score < 0.35:
        return "Lower"
    if score < 0.60:
        return "Moderate"
    if score < 0.80:
        return "High"
    return "Very high"

def compute_risk(occ, context, axis_scores, device_access, digital_access):
    base = occ["exposure"]
    calibration = context["automation_calibration"]

    digital_support = 0
    if occ["cognitive"] >= 0.5:
        digital_support += 0.05 * digital_access
    if occ["occupation"] in ["Bookkeeping / admin assistant", "Retail sales / market trader"]:
        digital_support += 0.04 * digital_access

    device_penalty = 0
    if device_access == "shared phone only":
        device_penalty += 0.03
    elif device_access == "feature phone":
        device_penalty += 0.05

    durable_buffer = (
        axis_scores.get("repair", 0) * 0.02 +
        axis_scores.get("care", 0) * 0.02 +
        axis_scores.get("craft", 0) * 0.02 +
        axis_scores.get("sales", 0) * 0.015 +
        axis_scores.get("logistics", 0) * 0.015
    )

    score = base * calibration + device_penalty - digital_support - durable_buffer
    score = float(np.clip(score, 0.0, 1.0))
    return {
        "score": round(score, 2),
        "level": risk_band(score),
        "base": round(base, 2),
        "calibration": round(calibration, 2),
        "device_penalty": round(device_penalty, 2),
        "digital_support": round(digital_support, 2),
        "durable_buffer": round(durable_buffer, 2)
    }

def adjacent_plan(occ, axis_scores):
    pool = list(occ["adjacent_skills"])
    if axis_scores.get("digital", 0) >= 2:
        pool += ["remote services", "online client communication"]
    if axis_scores.get("sales", 0) >= 2:
        pool += ["pricing", "customer retention"]
    if axis_scores.get("admin", 0) >= 2:
        pool += ["digital records", "spreadsheet workflows"]
    out = []
    for x in pool:
        if x not in out:
            out.append(x)
    return out[:5]

def explain_match(occ, matched, context):
    if matched:
        return (
            f"Matched because the input mentioned: {', '.join(sorted(set(matched[:5])))}. "
            f"This is coherent with a {context['context_name']} setting, where informal work often contains real but uncredentialed skill."
        )
    return (
        "No strong keyword hit was found, so the app used the closest occupation family in the graph. "
        "That keeps the profile readable instead of pretending to know more than the input supports."
    )

def opportunity_rows(occ, context, axis_scores, risk, goal_text):
    rows = []
    goal_text = clean_text(goal_text)
    for item in occ["opportunities"]:
        fit = 50
        low = item.lower()
        if "training" in low or "apprenticeship" in low:
            fit += 10
        if "micro" in low or "workshop" in low or "enterprise" in low:
            fit += 8
        if "digital" in low and axis_scores.get("digital", 0) >= 1.5:
            fit += 10
        if "agri" in low and ("farm" in goal_text or "agric" in goal_text):
            fit += 10
        if risk["level"] in ["High", "Very high"] and ("training" in low or "apprenticeship" in low):
            fit += 8

        rows.append({
            "Opportunity": item,
            "Opportunity type": (
                "training" if ("training" in low or "apprenticeship" in low) else
                "self-employment" if ("micro" in low or "shop" in low or "workshop" in low or "enterprise" in low) else
                "formal employment" if ("technician" in low or "assistant" in low or "associate" in low) else
                "gig / informal" if ("gig" in low or "delivery" in low) else
                "pathway"
            ),
            "Reachability score": int(np.clip(fit, 1, 100)),
            "Why it appears": context["constraint"]
        })
    df = pd.DataFrame(rows).sort_values("Reachability score", ascending=False).reset_index(drop=True)
    return df.head(5)


# OPTIONAL DATA HOOKS


def load_automation_table(path):
    if path and isinstance(path, str) and os.path.exists(path):
        try:
            df = pd.read_csv(path)
            df.columns = [c.strip().lower() for c in df.columns]
            if "occupation" not in df.columns or "exposure" not in df.columns:
                raise ValueError("Need occupation and exposure columns.")
            for c in ["routine", "manual", "cognitive"]:
                if c not in df.columns:
                    df[c] = np.nan
            return df, "Custom automation dataset loaded."
        except Exception:
            pass

    # built-in fallback
    df = pd.DataFrame([
        {
            "occupation": x["occupation"],
            "exposure": x["exposure"],
            "routine": x["routine"],
            "manual": x["manual"],
            "cognitive": x["cognitive"]
        } for x in OCCUPATIONS
    ])
    return df, "Built-in starter automation table. Replace with Frey-Osborne / ILO / STEP / custom CSV."

def load_wcde_projection(path):
    if path and isinstance(path, str) and os.path.exists(path):
        try:
            df = pd.read_csv(path)
            df.columns = [c.strip().lower() for c in df.columns]
            if "country" not in df.columns or "year" not in df.columns:
                raise ValueError("Expected at least country and year columns.")
            return df, "WCDE projection file loaded."
        except Exception:
            pass
    return pd.DataFrame(), "No WCDE CSV uploaded yet. Upload a Wittgenstein Centre export to activate this layer."


# CHARTS


def skill_radar(axis_scores):
    labels = ["repair", "sales", "digital", "care", "craft", "agri", "logistics", "admin"]
    values = [axis_scores.get(k, 0) for k in labels]
    values += values[:1]
    labels += labels[:1]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=labels, fill="toself", name="Skill intensity"))
    fig.update_layout(
        height=360,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        polar=dict(radialaxis=dict(visible=True, range=[0, 5]))
    )
    return fig

def risk_gauge(risk_score, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score * 100,
        title={"text": title},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#10b981" if risk_score < 0.35 else "#f59e0b" if risk_score < 0.6 else "#ef4444"},
            "steps": [
                {"range": [0, 35], "color": "rgba(16,185,129,0.16)"},
                {"range": [35, 60], "color": "rgba(245,158,11,0.16)"},
                {"range": [60, 80], "color": "rgba(239,68,68,0.16)"},
                {"range": [80, 100], "color": "rgba(124,58,237,0.16)"},
            ],
        }
    ))
    fig.update_layout(height=290, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def opportunity_chart(df):
    if df.empty:
        return go.Figure()
    fig = px.bar(
        df.sort_values("Reachability score", ascending=True),
        x="Reachability score",
        y="Opportunity",
        color="Opportunity type",
        orientation="h",
        height=360
    )
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), legend_title_text="")
    return fig

def signals_chart(df):
    plot_df = df.copy()
    plot_df["display_value"] = plot_df.apply(lambda r: normalize_for_chart(r["signal"], r["value"]), axis=1)
    fig = px.bar(
        plot_df.sort_values("display_value", ascending=True),
        x="display_value",
        y="signal",
        orientation="h",
        height=360,
        labels={"display_value": "Visible signal (scaled for chart)", "signal": ""}
    )
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
    return fig

def wcde_chart(df):
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Upload a WCDE CSV export to display education projections.",
            x=0.5, y=0.5, showarrow=False, font=dict(size=16)
        )
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        return fig

    numeric_cols = [c for c in df.columns if c not in ["country", "year"] and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        fig = go.Figure()
        fig.add_annotation(
            text="WCDE file loaded, but no numeric projection columns were found.",
            x=0.5, y=0.5, showarrow=False, font=dict(size=16)
        )
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        return fig

    cols = numeric_cols[:2]
    fig = go.Figure()
    for c in cols:
        fig.add_trace(go.Scatter(
            x=df["year"],
            y=df[c],
            mode="lines+markers",
            name=c.replace("_", " ").title()
        ))
    fig.update_layout(
        title="WCDE projection trend",
        height=320,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


# HTML RENDERERS


def format_signals_html(df, country_name):
    lines = []
    for _, r in df.iterrows():
        if r["value"] is None or pd.isna(r["value"]):
            v = "Not available"
        elif "GDP per capita" in r["signal"]:
            v = as_money(r["value"])
        else:
            v = as_percent(r["value"])
        lines.append(f"<li><b>{r['signal']}</b>: {v} <span class='small'>({r['year']})</span></li>")
    return f"""
    <div class="card">
        <div class="section-title">Visible labour signals for {country_name}</div>
        <div class="small">These are pulled from the World Bank API.</div>
        <hr class="soft">
        <ul style="line-height:1.8; padding-left: 20px; margin: 0;">
            {''.join(lines)}
        </ul>
    </div>
    """

def format_profile_html(occ, matched, explanation, portable_score, axis_scores, durable, adjacent, context):
    return f"""
    <div class="card">
        <div>
            <span class="badge">{context['tag']}</span>
            <span class="badge">{occ['taxonomy_family']}</span>
        </div>
        <div class="section-title" style="margin-top:8px;">Portable skills profile: {occ['occupation']}</div>
        <div class="callout"><b>Why this match:</b> {explanation}</div>
        <p style="line-height:1.6; margin-top:10px;">
            This profile names the occupation family, the strongest transferable skills,
            and the adjacent skills that would actually increase resilience.
        </p>
        <p class="small"><b>Matched keywords:</b> {', '.join(sorted(set(matched))) if matched else 'none'}</p>
        <p class="small"><b>Portability score:</b> {portable_score}/100</p>
        <p><b>Durable skills:</b><br>{badge_list(durable)}</p>
        <p><b>Adjacent skills to build next:</b><br>{badge_list(adjacent)}</p>
        <p class="small"><b>Axis strengths:</b> {axis_scores}</p>
    </div>
    """

def format_risk_html(risk, occ, context):
    return f"""
    <div class="card">
        <div class="section-title">AI readiness & displacement risk</div>
        <div class="callout"><b>Risk level:</b> {risk['level']} — {int(risk['score']*100)}/100</div>
        <p style="line-height:1.6; margin-top:10px;">
            The score starts from the occupation's base exposure and is adjusted for the local context calibration,
            device access, digital access, and the person's durable skills.
        </p>
        <p class="small">
            Base exposure = {risk['base']} · Calibration = {risk['calibration']} · Device penalty = {risk['device_penalty']}
            · Digital support = {risk['digital_support']} · Durable buffer = {risk['durable_buffer']}
        </p>
        <div class="warn"><b>Important:</b> this is a directional planning lens, it is not a judgment of worth or ability.</div>
        <p class="small">Context: {context['context_name']}</p>
    </div>
    """

def format_policy_html(context, alt_context, wcde_note):
    return f"""
    <div class="card-dark">
        <div class="section-title" style="color:#ffffff;">Country-agnostic reconfiguration</div>
        <p style="line-height:1.6; color:#e5e7eb;">
            Current context: <b>{context['tag']}</b><br>
            Swap-ready context: <b>{alt_context['tag']}</b>
        </p>
        <p style="line-height:1.6; color:#e5e7eb;">
            The codebase does not hardcode a country. It swaps the labour signal source, the education taxonomy label,
            the automation calibration, the language setting, and the set of opportunity types through configuration.
        </p>
        <div class="callout" style="color:#0f172a;">
            <b>WCDE layer:</b> {wcde_note}
        </div>
    </div>
    """

def format_hero_html(context, occ, portable_score, risk):
    return f"""
    <div class="card">
        <div id="hero">
            <h1>UNMAPPED</h1>
            <p>
                Open skills infrastructure for young people with real skills and missing signals.
                Built to map informal ability into portable profiles, expose honest labour-market risk,
                and surface realistic opportunities in low- and middle-income country contexts.
            </p>
        </div>
        <hr class="soft">
        <div>
            <span class="badge">{context['tag']}</span>
            <span class="badge">best match: {occ['occupation']}</span>
            <span class="badge">portability: {portable_score}/100</span>
            <span class="badge">risk: {risk['level']}</span>
        </div>
    </div>
    """

def kpi_html(portable_score, risk, signals_df, opp_df):
    # simple visible KPI strip
    neet = signals_df.loc[signals_df["signal"] == "Youth NEET (%)", "value"].iloc[0] if not signals_df.empty else None
    internet = signals_df.loc[signals_df["signal"] == "Internet users (% population)", "value"].iloc[0] if not signals_df.empty else None
    gdp = signals_df.loc[signals_df["signal"] == "GDP per capita (current US$)", "value"].iloc[0] if not signals_df.empty else None
    return f"""
    <div class="card">
        <div class="section-title">At-a-glance</div>
        <div class="kpi"><div class="label">Portability</div><div class="value">{portable_score}/100</div><div class="sub">How transferable the profile is</div></div>
        <div class="kpi"><div class="label">Risk</div><div class="value">{risk['level']}</div><div class="sub">{int(risk['score']*100)}/100 displacement lens</div></div>
        <div class="kpi"><div class="label">NEET</div><div class="value">{as_percent(neet)}</div><div class="sub">Visible labour signal</div></div>
        <div class="kpi"><div class="label">Internet access</div><div class="value">{as_percent(internet)}</div><div class="sub">Digital readiness constraint</div></div>
        <div class="kpi"><div class="label">GDP per capita</div><div class="value">{as_money(gdp)}</div><div class="sub">Economic context</div></div>
        <div class="kpi"><div class="label">Opportunities</div><div class="value">{len(opp_df)}</div><div class="sub">Ranked pathways shown</div></div>
    </div>
    """


# SAMPLE / PREFILL


def load_amara_sample():
    return (
        "ghana_urban",
        "English",
        "Secondary school certificate",
        "Self-taught coding from YouTube and informal phone repair apprenticeship",
        "Running a phone repair business since age 17",
        "screen replacement, battery diagnostics, customer handling, cash management, basic coding, troubleshooting",
        "English; Twi; Ga",
        2,
        "shared phone only",
        "Find realistic paid work and a stronger pathway to income without pretending to be something else",
        None,
        None
    )


# ANALYSIS PIPELINE


def analyze(
    context_key,
    ui_language,
    education_level,
    credential_text,
    experience_text,
    competencies_text,
    languages_text,
    digital_access,
    device_access,
    goal_text,
    automation_file_path,
    wcde_file_path
):
    context = COUNTRY_PACKS[context_key]
    alt_context = COUNTRY_PACKS[SWAP_CONTEXT[context_key]]
    lang = ui_language

    profile_text = " ".join([
        education_level or "",
        credential_text or "",
        experience_text or "",
        competencies_text or "",
        languages_text or "",
        goal_text or ""
    ])

    signals_df = fetch_wdi(context["country_code"], context["country_name"])
    automation_df, automation_note = load_automation_table(automation_file_path)
    wcde_df, wcde_note = load_wcde_projection(wcde_file_path)

    axis_scores = infer_axes(competencies_text, experience_text, goal_text)
    (best_score, occ, matched), ranking = best_occupation(profile_text)
    portable = portability_score(axis_scores)
    durable = occ["durable_skills"]
    adjacent = adjacent_plan(occ, axis_scores)
    risk = compute_risk(occ, context, axis_scores, device_access, digital_access)

    explanation = explain_match(occ, matched, context)
    opp_df = opportunity_rows(occ, context, axis_scores, risk, goal_text)

    # charts
    radar = skill_radar(axis_scores)
    risk_fig = risk_gauge(risk["score"], f"{occ['occupation']} risk")
    opp_fig = opportunity_chart(opp_df)
    sig_fig = signals_chart(signals_df)
    wcde_fig = wcde_chart(wcde_df)

    # tables
    signals_table = signals_df.copy()
    opp_table = opp_df.copy()

    debug_df = pd.DataFrame([{
        "matched_occupation": occ["occupation"],
        "taxonomy_family": occ["taxonomy_family"],
        "matched_keywords": ", ".join(sorted(set(matched))) if matched else "none",
        "portable_profile_score": portable,
        "risk_score": risk["score"],
        "risk_level": risk["level"],
        "durable_skills": ", ".join(durable),
        "adjacent_skills": ", ".join(adjacent),
    }])

    compare_df = pd.DataFrame([
        {
            "Context": context["tag"],
            "Country code": context["country_code"],
            "Automation calibration": context["automation_calibration"],
            "Opportunity types": ", ".join(context["opportunity_types"]),
            "Constraint": context["constraint"],
        },
        {
            "Context": alt_context["tag"],
            "Country code": alt_context["country_code"],
            "Automation calibration": alt_context["automation_calibration"],
            "Opportunity types": ", ".join(alt_context["opportunity_types"]),
            "Constraint": alt_context["constraint"],
        }
    ])

    hero_html = format_hero_html(context, occ, portable, risk)
    kpis = kpi_html(portable, risk, signals_df, opp_df)
    profile_html = format_profile_html(occ, matched, explanation, portable, axis_scores, durable, adjacent, context)
    risk_html = format_risk_html(risk, occ, context)
    signals_html = format_signals_html(signals_df, context["country_name"])
    policy_html = format_policy_html(context, alt_context, wcde_note)

    return (
        hero_html,
        kpis,
        profile_html,
        radar,
        opp_table,
        opp_fig,
        risk_html,
        risk_fig,
        signals_html,
        signals_table,
        sig_fig,
        policy_html,
        compare_df,
        wcde_fig,
        debug_df,
        automation_df.head(12)
    )


# UI


with gr.Blocks(css=CSS, theme=gr.themes.Soft(primary_hue="emerald", secondary_hue="slate", neutral_hue="slate")) as demo:
    gr.HTML("""
    <div class="card">
      <div id="hero">
        <h1>UNMAPPED</h1>
        <p>
          A prototype for skills recognition, AI displacement risk, and opportunity matching.
          It is designed as infrastructure: configurable by country, language, education taxonomy, and labour market data inputs.
        </p>
      </div>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Profile inputs")

            context_key = gr.Dropdown(
                choices=list(COUNTRY_PACKS.keys()),
                value="ghana_urban",
                label="Context pack",
                info="Swap Ghana / urban informal with India / rural agricultural without changing code."
            )
            ui_language = gr.Dropdown(
                choices=["English", "Français"],
                value="English",
                label="UI language"
            )
            education_level = gr.Textbox(label="Education level", placeholder="e.g., secondary school certificate")
            credential_text = gr.Textbox(label="Credentials / training", placeholder="e.g., self-taught coding from YouTube, informal apprenticeship")
            experience_text = gr.Textbox(label="Work experience", placeholder="e.g., running a phone repair business since age 17")
            competencies_text = gr.Textbox(label="Demonstrated competencies", lines=3, placeholder="e.g., screen replacement, battery diagnostics, customer handling, cash management, basic coding")
            languages_text = gr.Textbox(label="Languages spoken", placeholder="e.g., English; Twi; Ga")
            digital_access = gr.Slider(0, 5, value=2, step=1, label="Digital access readiness", info="0 = none, 5 = strong")
            device_access = gr.Dropdown(
                choices=["feature phone", "shared phone only", "smartphone", "smartphone + laptop"],
                value="shared phone only",
                label="Device access"
            )
            goal_text = gr.Textbox(label="What the person wants next", lines=2, placeholder="e.g., increase income, get training, find realistic work")
            automation_file_path = gr.File(label="Optional automation CSV upload", file_types=[".csv"], type="filepath")
            wcde_file_path = gr.File(label="Optional WCDE CSV upload", file_types=[".csv"], type="filepath")

            with gr.Row():
                run_btn = gr.Button("Run UNMAPPED analysis", variant="primary")
                sample_btn = gr.Button("Load Amara example", variant="secondary")

            gr.Markdown(
                """
                <div class="card">
                  <b>What this shows:</b> portable skills recognition, honest automation risk, visible econometric signals, and country-agnostic reconfiguration.
                </div>
                """
            )

        with gr.Column(scale=1.25):
            hero_out = gr.HTML()
            kpi_out = gr.HTML()

            with gr.Tabs():
                with gr.Tab("Youth profile"):
                    profile_out = gr.HTML()
                    radar_out = gr.Plot()
                    opp_df_out = gr.Dataframe(label="Ranked opportunities", wrap=True)
                    opp_fig_out = gr.Plot()

                with gr.Tab("AI readiness & risk"):
                    risk_out = gr.HTML()
                    risk_fig_out = gr.Plot()
                    signals_out = gr.HTML()
                    signals_df_out = gr.Dataframe(label="Visible labour signals", wrap=True)
                    signals_fig_out = gr.Plot()

                with gr.Tab("Policy / reconfiguration"):
                    policy_out = gr.HTML()
                    compare_df_out = gr.Dataframe(label="Context comparison", wrap=True)
                    wcde_fig_out = gr.Plot()
                    debug_out = gr.Dataframe(label="Debug readout", wrap=True)
                    automation_preview_out = gr.Dataframe(label="Automation table preview", wrap=True)

    run_btn.click(
        fn=analyze,
        inputs=[
            context_key,
            ui_language,
            education_level,
            credential_text,
            experience_text,
            competencies_text,
            languages_text,
            digital_access,
            device_access,
            goal_text,
            automation_file_path,
            wcde_file_path
        ],
        outputs=[
            hero_out,
            kpi_out,
            profile_out,
            radar_out,
            opp_df_out,
            opp_fig_out,
            risk_out,
            risk_fig_out,
            signals_out,
            signals_df_out,
            signals_fig_out,
            policy_out,
            compare_df_out,
            wcde_fig_out,
            debug_out,
            automation_preview_out
        ]
    )

    sample_btn.click(
        fn=load_amara_sample,
        inputs=[],
        outputs=[
            context_key,
            ui_language,
            education_level,
            credential_text,
            experience_text,
            competencies_text,
            languages_text,
            digital_access,
            device_access,
            goal_text,
            automation_file_path,
            wcde_file_path
        ]
    )

    gr.HTML("""
    <div class="card">
      <div class="section-title">Demo guidance</div>
      <div class="small">
        1) Load the Amara example or Customize the fields. 2) Run the analysis. 3) Switch context pack to show localizability. 4) Upload a real automation CSV or WCDE export if available.
        
      </div>
    </div>
    """)

demo.launch()