import streamlit as st
import pandas as pd
import numpy as np
import uuid
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="AMR-PULSE", page_icon="🧬", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# -------------------- Session state --------------------
for key, value in {
    "patient_id": "",
    "patient_profile": {},
    "test_recommendations": [],
    "sensor_results": [],
    "amr_profile": [],
    "analysis_run": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------- Data helpers --------------------
def read_csv(path):
    try:
        if Path(path).exists():
            return pd.read_csv(path, low_memory=False)
    except Exception:
        pass
    return pd.DataFrame()

def make_patient_id():
    return "AMP-" + datetime.now().strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6].upper()

def who_master():
    return read_csv(DATA_DIR / "amr" / "processed" / "AMR_PULSE_WHO_GLASS_2023_Master.csv")

def who_timeseries():
    return read_csv(DATA_DIR / "amr" / "processed" / "WHO_GLASS_Acinetobacter_Amikacin_TimeSeries_2018_2023.csv")

def card():
    return read_csv(DATA_DIR / "amr" / "processed" / "CARD_AMR_Master.csv")

def amrfinder():
    return read_csv(DATA_DIR / "amr" / "processed" / "AMRFinderPlus_AMR_Master.csv")

def resfinder():
    return read_csv(DATA_DIR / "amr" / "processed" / "ResFinder_AMR_Master.csv")

def ncbi_phage():
    return read_csv(DATA_DIR / "phage" / "processed" / "NCBI_Ecoli_phage_Master.csv")

def ictv():
    return read_csv(DATA_DIR / "phage" / "processed" / "ICTV" / "ICTV_Virus_Master.csv")

def tests_for_site(site):
    mapping = {
        "Urinary tract infection": ["Urine culture", "Organism identification", "AST"],
        "Bloodstream infection": ["Blood culture", "Organism identification", "AST"],
        "Respiratory infection": ["Appropriate respiratory specimen culture", "Organism identification", "AST"],
        "Wound / skin infection": ["Wound / specimen culture", "Organism identification", "AST"],
        "Gastrointestinal infection": ["Stool / appropriate specimen culture", "Organism identification", "AST"],
    }
    return mapping.get(site, ["Appropriate specimen testing", "Organism identification", "AST"])

def antibiotics_for(organism):
    if organism == "Escherichia coli":
        return ["Ampicillin", "Cefepime", "Cefotaxime", "Ceftazidime",
                "Ceftriaxone", "Ciprofloxacin", "Co-trimoxazole", "Colistin"]
    if organism == "Acinetobacter spp.":
        return ["Amikacin", "Colistin", "Doripenem", "Gentamicin",
                "Imipenem", "Meropenem", "Minocycline", "Tigecycline"]
    return ["Ampicillin", "Ceftriaxone", "Ciprofloxacin", "Gentamicin",
            "Amikacin", "Meropenem", "Imipenem", "Colistin"]

def normalize_od(negative, positive, sample):
    return (sample - negative) / (positive - negative)

def classify(normalized):
    # DEMONSTRATION ONLY. Replace with validated sensor/AST model.
    if normalized <= 0.30:
        return "Susceptible", "🟢"
    if normalized <= 0.70:
        return "Intermediate", "🟡"
    return "Resistant", "🔴"

def ast_priority(organism, previous):
    previous = {x.lower() for x in previous}
    rows = []
    for drug in antibiotics_for(organism):
        exposed = drug.lower() in previous
        rows.append({
            "Antibiotic": drug,
            "Previous exposure": "Yes" if exposed else "No",
            "AST priority": "High" if exposed else "Routine",
            "Rationale": "Previous exposure flagged" if exposed else "Organism/surveillance panel"
        })
    return pd.DataFrame(rows)

def forecast(organism, antibiotic):
    df = who_timeseries()
    if df.empty or organism != "Acinetobacter spp." or antibiotic != "Amikacin":
        return None
    if "Year" not in df or "Median" not in df:
        return None
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Median"] = pd.to_numeric(df["Median"], errors="coerce")
    df = df.dropna(subset=["Year", "Median"])
    if len(df) < 3:
        return None
    x, y = df["Year"].to_numpy(float), df["Median"].to_numpy(float)
    slope, intercept = np.polyfit(x, y, 1)
    years = np.arange(int(x.max()) + 1, int(x.max()) + 4)
    projected = slope * years + intercept
    return df[["Year", "Median"]], pd.DataFrame({"Year": years, "Median": projected}), slope

def phage_candidates(organism):
    if organism == "Escherichia coli":
        df = ncbi_phage()
        if not df.empty and "host_name" in df:
            return df[df["host_name"].astype(str).str.contains("Escherichia coli", case=False, na=False)]
    elif organism == "Acinetobacter spp.":
        df = ictv()
        if not df.empty and "Host source" in df:
            return df[df["Host source"].astype(str).str.contains("bacteria", case=False, na=False)]
    return pd.DataFrame()

# -------------------- Header --------------------
st.title("🧬 AMR-PULSE")
st.subheader("AI-Powered Rapid AMR Profiling & Decision Support")
st.write("Patient → local AMR trends → AST prioritization → sensor testing → "
         "patient-specific AMR Profile → AMR Passport → forecast → decision support → phage review.")
st.warning("RESEARCH / HACKATHON PROTOTYPE ONLY. Demonstration S/I/R thresholds and forecasts are not validated clinical criteria.")

# ==========================================================
# 1. PATIENT + CLINICAL INPUT
# ==========================================================
st.markdown("---")
st.header("1️⃣ Patient & Clinical Details")

c1, c2, c3 = st.columns(3)
with c1:
    patient_name = st.text_input("Patient / Sample name", placeholder="Optional")
with c2:
    age = st.number_input("Age", 0, 120, 25)
with c3:
    sex = st.selectbox("Sex", ["Select", "Male", "Female", "Other / Not specified"])

c1, c2 = st.columns(2)
with c1:
    country = st.text_input("Country", "India")
with c2:
    area = st.text_input("Local area / State / District", placeholder="e.g. Hyderabad / Telangana")

infection_site = st.selectbox("Suspected infection site", [
    "Select", "Urinary tract infection", "Bloodstream infection",
    "Respiratory infection", "Wound / skin infection",
    "Gastrointestinal infection", "Other / unspecified"
])
symptoms = st.text_area("Symptoms / clinical information")
concerns = st.multiselect("Patient concerns / factors to flag", [
    "Drug allergy concern", "Previous treatment failure", "Recent hospitalization",
    "Recent antibiotic exposure", "Renal function concern", "Hepatic function concern",
    "Pregnancy / reproductive consideration", "Immunocompromised status", "Other clinical concern"
])
previous_antibiotics = st.multiselect("Previous / current antibiotics", [
    "Amoxicillin", "Amoxicillin-clavulanate", "Ceftriaxone", "Cefixime",
    "Cefepime", "Ceftazidime", "Ciprofloxacin", "Levofloxacin",
    "Azithromycin", "Doxycycline", "Piperacillin-tazobactam",
    "Meropenem", "Imipenem", "Amikacin", "Gentamicin", "Colistin",
    "Other / unknown", "No previous antibiotic exposure"
])

# ==========================================================
# 2. INITIAL AI / TREND ANALYSIS + AST PRIORITY
# ==========================================================
st.markdown("---")
st.header("2️⃣ Initial AMR Analysis & AST Prioritization")

if st.button("🧠 Analyze Patient + Local AMR Trends", type="primary"):
    if infection_site == "Select":
        st.error("Select the suspected infection site.")
    elif not symptoms.strip():
        st.warning("Enter symptoms / clinical information.")
    else:
        st.session_state.patient_id = make_patient_id()
        st.session_state.patient_profile = {
            "Patient Unique ID": st.session_state.patient_id,
            "Patient / Sample": patient_name or "Not entered",
            "Age": age, "Sex": sex, "Country": country or "Not specified",
            "Local Area": area or "Not specified",
            "Infection Site": infection_site, "Symptoms": symptoms,
            "Previous Antibiotics": ", ".join(previous_antibiotics) or "None entered",
            "Patient Concerns": ", ".join(concerns) or "None entered"
        }
        st.session_state.test_recommendations = tests_for_site(infection_site)
        st.session_state.analysis_run = True

if st.session_state.analysis_run:
    st.success(f"Patient Unique ID: **{st.session_state.patient_id}**")

    st.subheader("📈 Local / Country AMR Trend Signal")
    who = who_master()
    if not who.empty and "PathogenName" in who.columns:
        trend_counts = who["PathogenName"].value_counts().rename_axis("Organism").to_frame("Surveillance records")
        st.bar_chart(trend_counts)
    else:
        st.info("WHO GLASS prototype data not found.")

    st.caption("The current WHO GLASS prototype file is a small surveillance subset. "
               "It is not sufficient to claim a patient-specific local resistance percentage. "
               "The entered area/country is retained as context.")

    st.subheader("🧪 Suggested AST Priority Panel")
    # At this stage organism is not yet confirmed, so show the two prototype organism panels.
    e_col, a_col = st.columns(2)
    with e_col:
        st.markdown("**If organism = E. coli**")
        st.dataframe(ast_priority("Escherichia coli", previous_antibiotics), use_container_width=True, hide_index=True)
    with a_col:
        st.markdown("**If organism = Acinetobacter spp.**")
        st.dataframe(ast_priority("Acinetobacter spp.", previous_antibiotics), use_container_width=True, hide_index=True)

    st.subheader("🔬 Suggested Diagnostic Tests")
    for test in st.session_state.test_recommendations:
        st.write("• " + test)

# ==========================================================
# 3. ORGANISM
# ==========================================================
st.markdown("---")
st.header("3️⃣ Organism Identification")

organism = st.selectbox("Laboratory-identified organism", [
    "Select", "Escherichia coli", "Acinetobacter spp."
])

if organism != "Select":
    st.success(f"Organism: **{organism}**")

# ==========================================================
# 4. SENSOR / AST RESULTS
# ==========================================================
if organism != "Select":
    st.markdown("---")
    st.header("4️⃣ Patient-Specific Sensor / AST Result")

    antibiotic = st.selectbox("Antibiotic tested", antibiotics_for(organism))

    c1, c2, c3 = st.columns(3)
    with c1:
        negative_od = st.number_input("Negative control OD", 0.0, 5.0, 0.00, 0.01, format="%.2f")
    with c2:
        positive_od = st.number_input("Positive control OD", 0.0, 5.0, 1.00, 0.01, format="%.2f")
    with c3:
        sample_od = st.number_input("Antibiotic sample OD", 0.0, 5.0, 0.00, 0.01, format="%.2f")

    if st.button("🧬 Analyze & Add to AMR Profile", type="primary"):
        if positive_od <= negative_od:
            st.error("Positive control OD must be greater than negative control OD.")
        else:
            norm = normalize_od(negative_od, positive_od, sample_od)
            result, icon = classify(norm)
            record = {
                "Patient Unique ID": st.session_state.patient_id or make_patient_id(),
                "Organism": organism, "Antibiotic": antibiotic,
                "Negative Control OD": negative_od, "Positive Control OD": positive_od,
                "Sample OD": sample_od, "Normalized Response": round(norm, 4),
                "AMR Classification": result,
                "Date": datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state.amr_profile = [
                x for x in st.session_state.amr_profile if x["Antibiotic"] != antibiotic
            ]
            st.session_state.amr_profile.append(record)
            st.session_state.sensor_results.append(record)
            st.success(f"{icon} Preliminary result: **{result}**")
            st.metric("Normalized sensor response", f"{norm:.2f}")
            st.caption("DEMONSTRATION ONLY: ≤0.30 Susceptible; >0.30–0.70 Intermediate; >0.70 Resistant.")

# ==========================================================
# 5. AMR PROFILE
# ==========================================================
st.markdown("---")
st.header("5️⃣ Current Patient-Specific AMR Profile")

if st.session_state.amr_profile:
    profile = pd.DataFrame(st.session_state.amr_profile)
    st.dataframe(profile, use_container_width=True, hide_index=True)

    counts = profile["AMR Classification"].value_counts()
    chart = pd.DataFrame({
        "Classification": ["Susceptible", "Intermediate", "Resistant"],
        "Count": [int(counts.get("Susceptible", 0)),
                  int(counts.get("Intermediate", 0)),
                  int(counts.get("Resistant", 0))]
    }).set_index("Classification")
    st.bar_chart(chart)
else:
    st.info("Add sensor / AST results for multiple antibiotics to build the AMR Profile.")

# ==========================================================
# 6. AMR PASSPORT
# ==========================================================
st.markdown("---")
st.header("6️⃣ AMR Passport")

if st.session_state.patient_profile:
    p = st.session_state.patient_profile
    st.subheader(f"🪪 Patient Unique ID: {p['Patient Unique ID']}")

    c1, c2 = st.columns(2)
    with c1:
        st.write("**Patient / Sample:**", p["Patient / Sample"])
        st.write("**Age:**", p["Age"])
        st.write("**Sex:**", p["Sex"])
        st.write("**Country:**", p["Country"])
        st.write("**Local Area:**", p["Local Area"])
    with c2:
        st.write("**Infection Site:**", p["Infection Site"])
        st.write("**Symptoms:**", p["Symptoms"])
        st.write("**Previous Antibiotics:**", p["Previous Antibiotics"])
        st.write("**Patient Concerns:**", p["Patient Concerns"])
        st.write("**Current Organism:**", organism)

    if st.session_state.amr_profile:
        st.subheader("Current AMR History")
        st.dataframe(pd.DataFrame(st.session_state.amr_profile), use_container_width=True, hide_index=True)
        csv = pd.DataFrame(st.session_state.amr_profile).to_csv(index=False).encode()
        st.download_button("⬇️ Download AMR Passport", csv,
                           f"{p['Patient Unique ID']}_AMR_Passport.csv", "text/csv")
else:
    st.info("Run the initial analysis to generate the patient-specific AMR Passport.")

# ==========================================================
# 7. FORECAST
# ==========================================================
st.markdown("---")
st.header("7️⃣ Future AMR Trend / Forecast")

if organism != "Select" and st.session_state.amr_profile:
    shown = False
    for rec in st.session_state.amr_profile:
        result = forecast(organism, rec["Antibiotic"])
        if result is not None:
            shown = True
            observed, projected, slope = result
            st.subheader(f"Surveillance outlook: {organism} / {rec['Antibiotic']}")
            observed = observed.rename(columns={"Median": "Observed"})
            projected = projected.rename(columns={"Median": "Projected"})
            combined = observed.merge(projected, on="Year", how="outer").set_index("Year")
            st.line_chart(combined)
            direction = "increasing" if slope > 0.001 else "decreasing" if slope < -0.001 else "approximately stable"
            st.write(f"**Prototype trend:** {direction}.")
            st.caption("This is a simple projection from the available prototype time series, not an individual patient prediction.")
    if not shown:
        st.info("No matching time-series dataset is currently available for this organism/antibiotic combination.")

# ==========================================================
# 8. REFERENCE DATABASE SUPPORT
# ==========================================================
st.markdown("---")
st.header("8️⃣ AMR Reference Database Support")

if organism != "Select" and st.session_state.amr_profile:
    rows = []
    c = card()
    a = amrfinder()
    r = resfinder()

    for rec in st.session_state.amr_profile:
        drug = rec["Antibiotic"]
        card_n = int(c["CARD_short_name"].astype(str).str.contains(drug, case=False, na=False).sum()) if not c.empty and "CARD_short_name" in c else 0
        if not a.empty:
            cols = [x for x in ["gene_family", "product_name", "class", "subclass"] if x in a.columns]
            mask = np.zeros(len(a), dtype=bool)
            for col in cols:
                mask |= a[col].astype(str).str.contains(drug, case=False, na=False)
            amr_n = int(mask.sum())
        else:
            amr_n = 0
        res_n = int(r["gene_family"].astype(str).str.contains(drug, case=False, na=False).sum()) if not r.empty and "gene_family" in r else 0
        rows.append({
            "Antibiotic": drug,
            "Current sensor result": rec["AMR Classification"],
            "CARD records": card_n,
            "AMRFinderPlus records": amr_n,
            "ResFinder records": res_n
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption("Reference database records are supporting knowledge; they do not independently predict this patient's phenotype.")

# ==========================================================
# 9. DECISION SUPPORT
# ==========================================================
st.markdown("---")
st.header("9️⃣ Clinical Decision Support")

if not st.session_state.amr_profile:
    st.info("Complete patient-specific sensor / AST results first.")
else:
    profile = pd.DataFrame(st.session_state.amr_profile)
    susceptible = profile.loc[profile["AMR Classification"] == "Susceptible", "Antibiotic"].tolist()
    intermediate = profile.loc[profile["AMR Classification"] == "Intermediate", "Antibiotic"].tolist()
    resistant = profile.loc[profile["AMR Classification"] == "Resistant", "Antibiotic"].tolist()

    if susceptible:
        st.subheader("💊 Potential antimicrobial options for review")
        for drug in susceptible:
            st.success(f"🟢 {drug} — susceptible in the prototype profile")
    else:
        st.warning("No tested antibiotic is classified as susceptible by the prototype model.")

    if resistant:
        st.subheader("🔁 Alternatives requiring review")
        if susceptible:
            for drug in susceptible:
                st.write(f"• {drug} — candidate for clinician/laboratory review based on current susceptible signal.")
        else:
            st.write("No susceptible alternative is present in the entered panel; broader AST may be required.")

    if intermediate:
        st.warning("Intermediate results requiring additional laboratory/clinical interpretation: " + ", ".join(intermediate))

    if concerns:
        st.subheader("⚠️ Patient concern flags")
        for concern in concerns:
            st.write(f"• {concern} — requires clinical review before treatment selection.")

    st.warning("The prototype does not prescribe. Final antimicrobial selection requires validated AST, organism/specimen context, allergies, organ function, interactions, local guidance and clinician/laboratory review.")

# ==========================================================
# 10. PHAGE THERAPY
# ==========================================================
st.markdown("---")
st.header("🔟 Phage Therapy Candidate Review")

if organism != "Select":
    candidates = phage_candidates(organism)
    if not candidates.empty:
        st.write(f"Host-associated research records available: **{len(candidates)}**")
        cols = [x for x in ["accession", "virus_name", "host_name", "completeness", "length", "release_date",
                            "Virus name(s)", "Host source", "Genome"] if x in candidates.columns]
        st.dataframe(candidates[cols].head(20), use_container_width=True, hide_index=True)
    else:
        st.info("No host-associated candidate records found in the current prototype dataset.")
    st.caption("Database matching does not prove lytic activity, therapeutic suitability, safety or clinical efficacy.")

# ==========================================================
# 11. DATABASE STATUS
# ==========================================================
st.markdown("---")
st.header("1️⃣1️⃣ AMR-PULSE Knowledge Base")

db_paths = [
    ("WHO GLASS", DATA_DIR / "amr" / "processed" / "AMR_PULSE_WHO_GLASS_2023_Master.csv"),
    ("CARD", DATA_DIR / "amr" / "processed" / "CARD_AMR_Master.csv"),
    ("AMRFinderPlus", DATA_DIR / "amr" / "processed" / "AMRFinderPlus_AMR_Master.csv"),
    ("ResFinder", DATA_DIR / "amr" / "processed" / "ResFinder_AMR_Master.csv"),
    ("NCBI Virus", DATA_DIR / "phage" / "processed" / "NCBI_Ecoli_phage_Master.csv"),
    ("PhagesDB", DATA_DIR / "phage" / "processed" / "PhagesDB_Phage_Master.csv"),
    ("PhageScope", DATA_DIR / "phage" / "processed" / "PhageScope" / "PhageScope_RefSeq_Phage_Master.csv"),
    ("ICTV", DATA_DIR / "phage" / "processed" / "ICTV" / "ICTV_Virus_Master.csv"),
]
rows = []
for name, path in db_paths:
    df = read_csv(path)
    rows.append({"Database": name, "Status": "Available" if path.exists() else "Not found", "Records": len(df)})
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ==========================================================
# 12. SESSION HISTORY
# ==========================================================
st.markdown("---")
st.header("1️⃣2️⃣ Sensor / AMR History")

if st.session_state.sensor_results:
    history = pd.DataFrame(st.session_state.sensor_results)
    st.dataframe(history, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export Sensor History CSV",
                       history.to_csv(index=False).encode(),
                       "AMR_PULSE_sensor_history.csv", "text/csv")
else:
    st.info("No sensor results recorded in this session.")

st.markdown("---")
st.caption("AMR-PULSE | Research / hackathon prototype | Not for clinical diagnosis or prescribing.")
