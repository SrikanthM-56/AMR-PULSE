import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# ==========================================================
# AMR-PULSE — AI-Powered Rapid AMR Profiling & Decision Support
# Prototype application
# ==========================================================

st.set_page_config(
    page_title="AMR-PULSE",
    page_icon="🧬",
    layout="wide"
)

# ----------------------------------------------------------
# Paths
# ----------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# ----------------------------------------------------------
# Session state
# ----------------------------------------------------------
if "sensor_results" not in st.session_state:
    st.session_state.sensor_results = []

if "test_recommendations" not in st.session_state:
    st.session_state.test_recommendations = []

if "amr_profile" not in st.session_state:
    st.session_state.amr_profile = []

# ----------------------------------------------------------
# Helper functions
# ----------------------------------------------------------
def safe_count(path):
    """Return row count for a CSV without crashing the app."""
    try:
        return len(pd.read_csv(path))
    except Exception:
        return 0


def classify_response(normalized_response):
    """
    Prototype-only demonstration classification.

    IMPORTANT:
    These are not clinical breakpoints. Replace this function with
    a validated OD-to-S/I/R model when labelled sensor + AST data
    become available.
    """
    susceptible_cutoff = 0.30
    intermediate_cutoff = 0.70

    if normalized_response <= susceptible_cutoff:
        return "Susceptible", "🟢"
    elif normalized_response <= intermediate_cutoff:
        return "Intermediate", "🟡"
    return "Resistant", "🔴"


def recommend_tests(infection_site):
    recommendations = {
        "Urinary tract infection": [
            "Urine culture",
            "Organism identification",
            "Antimicrobial susceptibility testing (AST)"
        ],
        "Bloodstream infection": [
            "Blood culture",
            "Organism identification",
            "Antimicrobial susceptibility testing (AST)"
        ],
        "Respiratory infection": [
            "Respiratory specimen culture",
            "Organism identification",
            "Antimicrobial susceptibility testing (AST)"
        ],
        "Wound / skin infection": [
            "Wound/swab culture",
            "Organism identification",
            "Antimicrobial susceptibility testing (AST)"
        ],
        "Gastrointestinal infection": [
            "Stool culture",
            "Organism identification",
            "Antimicrobial susceptibility testing (AST)"
        ],
    }
    return recommendations.get(
        infection_site,
        ["Culture / appropriate diagnostic testing",
         "Organism identification",
         "Antimicrobial susceptibility testing (AST)"]
    )


def database_status():
    files = {
        "WHO GLASS": DATA_DIR / "amr" / "processed" / "AMR_PULSE_WHO_GLASS_2023_Master.csv",
        "CARD": DATA_DIR / "amr" / "processed" / "CARD_AMR_Master.csv",
        "AMRFinderPlus": DATA_DIR / "amr" / "processed" / "AMRFinderPlus_AMR_Master.csv",
        "ResFinder": DATA_DIR / "amr" / "processed" / "ResFinder_AMR_Master.csv",
        "NCBI Virus": DATA_DIR / "phage" / "processed" / "NCBI_Ecoli_phage_Master.csv",
        "PhagesDB": DATA_DIR / "phage" / "processed" / "PhagesDB_Phage_Master.csv",
        "PhageScope": DATA_DIR / "phage" / "processed" / "PhageScope" / "PhageScope_RefSeq_Phage_Master.csv",
        "ICTV": DATA_DIR / "phage" / "processed" / "ICTV" / "ICTV_Virus_Master.csv",
    }

    rows = []
    for name, path in files.items():
        rows.append({
            "Database": name,
            "Status": "Available" if path.exists() else "Not found",
            "Records": safe_count(path) if path.exists() else 0
        })
    return pd.DataFrame(rows)


# ==========================================================
# Header
# ==========================================================
st.title("🧬 AMR-PULSE")
st.subheader("AI-Powered Rapid AMR Profiling & Decision Support")

st.info(
    "Prototype workflow: Patient information → symptoms → diagnostic test "
    "recommendation → organism identification → sensor response → "
    "AMR analysis → AMR Profile → AMR Passport → clinical decision support."
)

st.warning(
    "RESEARCH PROTOTYPE ONLY — This application is not a clinical diagnostic "
    "or prescribing tool. S/I/R thresholds shown in this prototype are "
    "demonstration values and must be replaced by validated experimental "
    "data and appropriate laboratory susceptibility criteria."
)

# ==========================================================
# 1. PATIENT DETAILS
# ==========================================================
st.markdown("---")
st.header("👤 1. Patient Details")

col1, col2, col3 = st.columns(3)

with col1:
    patient_name = st.text_input("Patient / Sample ID", placeholder="Enter sample ID")

with col2:
    age = st.number_input("Age", min_value=0, max_value=120, value=25, step=1)

with col3:
    sex = st.selectbox("Sex", ["Select", "Male", "Female", "Other / Not specified"])

# ==========================================================
# 2. CLINICAL INFORMATION
# ==========================================================
st.markdown("---")
st.header("🩺 2. Clinical Information")

infection_site = st.selectbox(
    "Suspected Infection Site",
    [
        "Select",
        "Urinary tract infection",
        "Bloodstream infection",
        "Respiratory infection",
        "Wound / skin infection",
        "Gastrointestinal infection",
        "Other / unspecified"
    ]
)

symptoms = st.text_area(
    "Symptoms / Clinical Information",
    placeholder="Enter relevant symptoms..."
)

# ==========================================================
# 3. PREVIOUS ANTIBIOTIC HISTORY
# ==========================================================
st.markdown("---")
st.header("💊 3. Previous Antibiotic History")

previous_antibiotics = st.multiselect(
    "Select antibiotics previously used / exposed to",
    [
        "Amoxicillin",
        "Amoxicillin-clavulanate",
        "Ceftriaxone",
        "Cefixime",
        "Ciprofloxacin",
        "Levofloxacin",
        "Azithromycin",
        "Doxycycline",
        "Piperacillin-tazobactam",
        "Meropenem",
        "Other / unknown",
        "No previous antibiotic exposure"
    ]
)

if previous_antibiotics:
    st.caption(
        "Previous antibiotic exposure is recorded as clinical context and "
        "can help prioritize laboratory testing. It does not by itself "
        "determine the patient's resistance status."
    )

# ==========================================================
# 4. DIAGNOSTIC TEST RECOMMENDATION
# ==========================================================
st.markdown("---")
st.header("🔬 4. Diagnostic Test Recommendation")

if st.button("🔎 Suggest Diagnostic Tests"):
    if infection_site == "Select":
        st.warning("Please select the suspected infection site first.")
    else:
        st.session_state.test_recommendations = recommend_tests(infection_site)

if st.session_state.test_recommendations:
    st.success("Suggested diagnostic workflow:")
    for test in st.session_state.test_recommendations:
        st.write(f"• {test}")

# ==========================================================
# 5. ORGANISM IDENTIFICATION
# ==========================================================
st.markdown("---")
st.header("🦠 5. Organism Identification")

st.info(
    "Enter the organism identified by the diagnostic laboratory. "
    "The prototype currently demonstrates the workflow using organisms "
    "represented in the AMR-PULSE reference data."
)

organism = st.selectbox(
    "Identified Organism",
    [
        "Select",
        "Escherichia coli",
        "Acinetobacter spp."
    ],
    index=0
)

if organism != "Select":
    st.success(f"Organism selected: {organism}")

# ==========================================================
# 6. SENSOR DATA
# ==========================================================
if organism != "Select":

    st.markdown("---")
    st.header("🧪 6. AMR-PULSE Sensor Sampling")

    st.info(
        "Enter the optical density (OD) measured for the negative control, "
        "positive control, and antibiotic-exposed patient isolate."
    )

    antibiotic_options = [
        "Select",
        "Ampicillin",
        "Ceftriaxone",
        "Cefepime",
        "Ceftazidime",
        "Ciprofloxacin",
        "Gentamicin",
        "Amikacin",
        "Meropenem",
        "Imipenem",
        "Colistin"
    ]

    # Keep only antibiotics represented in the selected organism's
    # prototype WHO GLASS subset where practical.
    if organism == "Escherichia coli":
        default_antibiotics = [
            "Select",
            "Ampicillin",
            "Cefepime",
            "Cefotaxime",
            "Ceftazidime",
            "Ceftriaxone",
            "Ciprofloxacin",
            "Co-trimoxazole",
            "Colistin"
        ]
        antibiotic_options = default_antibiotics
    elif organism == "Acinetobacter spp.":
        antibiotic_options = [
            "Select",
            "Amikacin",
            "Colistin",
            "Doripenem",
            "Gentamicin",
            "Imipenem",
            "Meropenem",
            "Minocycline",
            "Tigecycline"
        ]

    antibiotic = st.selectbox(
        "Select Antibiotic",
        antibiotic_options,
        index=0
    )

    st.markdown("### 📊 Sensor Sampling")

    col1, col2, col3 = st.columns(3)

    with col1:
        negative_od = st.number_input(
            "Negative Control OD",
            min_value=0.0,
            max_value=5.0,
            value=0.00,
            step=0.01,
            format="%.2f"
        )

    with col2:
        positive_od = st.number_input(
            "Positive Control OD",
            min_value=0.0,
            max_value=5.0,
            value=1.00,
            step=0.01,
            format="%.2f"
        )

    with col3:
        sample_od = st.number_input(
            "Antibiotic Sample OD",
            min_value=0.0,
            max_value=5.0,
            value=0.00,
            step=0.01,
            format="%.2f"
        )

    if st.button("💾 Analyze & Record Sensor Result"):

        if antibiotic == "Select":
            st.warning("Please select an antibiotic.")

        elif positive_od <= negative_od:
            st.warning(
                "Positive control OD must be greater than negative control OD."
            )

        elif sample_od == 0.0:
            st.warning("Please enter the antibiotic sample OD.")

        else:
            normalized_response = (
                (sample_od - negative_od)
                / (positive_od - negative_od)
            )

            amr_result, result_icon = classify_response(normalized_response)

            record = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Patient / Sample ID": patient_name if patient_name else "Not entered",
                "Organism": organism,
                "Antibiotic": antibiotic,
                "Negative Control OD": negative_od,
                "Positive Control OD": positive_od,
                "Sample OD": sample_od,
                "Normalized Response": round(normalized_response, 4),
                "AMR Result": amr_result
            }

            st.session_state.sensor_results.append(record)

            # Update the current AMR profile: one latest result per antibiotic.
            st.session_state.amr_profile = [
                r for r in st.session_state.amr_profile
                if r["Antibiotic"] != antibiotic
            ]

            st.session_state.amr_profile.append({
                "Antibiotic": antibiotic,
                "Sample OD": round(sample_od, 4),
                "Normalized Response": round(normalized_response, 4),
                "AMR Classification": amr_result
            })

            st.success(
                f"Sensor result recorded for {antibiotic}."
            )

            st.metric(
                "Normalized Sensor Response",
                f"{normalized_response:.2f}"
            )

            st.subheader(
                f"{result_icon} Preliminary Result: {amr_result}"
            )

            st.caption(
                "Prototype demonstration thresholds: "
                "≤ 0.30 = Susceptible | "
                "> 0.30 to ≤ 0.70 = Intermediate | "
                "> 0.70 = Resistant."
            )

# ==========================================================
# 7. AMR PROFILE
# ==========================================================
st.markdown("---")
st.header("📋 7. AMR Profile")

if st.session_state.amr_profile:

    profile_df = pd.DataFrame(st.session_state.amr_profile)

    st.dataframe(
        profile_df,
        use_container_width=True,
        hide_index=True
    )

    susceptible_count = sum(
        r["AMR Classification"] == "Susceptible"
        for r in st.session_state.amr_profile
    )
    intermediate_count = sum(
        r["AMR Classification"] == "Intermediate"
        for r in st.session_state.amr_profile
    )
    resistant_count = sum(
        r["AMR Classification"] == "Resistant"
        for r in st.session_state.amr_profile
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🟢 Susceptible", susceptible_count)

    with col2:
        st.metric("🟡 Intermediate", intermediate_count)

    with col3:
        st.metric("🔴 Resistant", resistant_count)

else:
    st.info(
        "Record sensor results for one or more antibiotics to build the "
        "patient's current AMR Profile."
    )

# ==========================================================
# 8. AMR PASSPORT
# ==========================================================
st.markdown("---")
st.header("🪪 8. AMR Passport")

st.info(
    "The AMR Passport is designed as a longitudinal record of the patient's "
    "current and previous AMR information."
)

passport_col1, passport_col2 = st.columns(2)

with passport_col1:
    st.write("**Patient / Sample ID:**", patient_name or "Not entered")
    st.write("**Age:**", age)
    st.write("**Sex:**", sex)
    st.write("**Current organism:**", organism)

with passport_col2:
    st.write("**Infection site:**", infection_site)
    st.write(
        "**Previous antibiotics:**",
        ", ".join(previous_antibiotics) if previous_antibiotics else "None entered"
    )
    st.write(
        "**Current AMR results:**",
        len(st.session_state.amr_profile)
    )

if st.session_state.amr_profile:
    st.markdown("### Current AMR History")
    passport_df = pd.DataFrame(st.session_state.amr_profile)
    st.dataframe(
        passport_df,
        use_container_width=True,
        hide_index=True
    )

# ==========================================================
# 9. CLINICAL DECISION SUPPORT
# ==========================================================
st.markdown("---")
st.header("🩺 9. Clinical Decision Support")

st.info(
    "This section provides research-oriented decision support using the "
    "current prototype AMR profile, organism, and database knowledge. "
    "It does not prescribe treatment."
)

if not st.session_state.amr_profile:
    st.warning(
        "Complete at least one sensor analysis before generating decision support."
    )
else:

    resistant_drugs = [
        r["Antibiotic"]
        for r in st.session_state.amr_profile
        if r["AMR Classification"] == "Resistant"
    ]

    susceptible_drugs = [
        r["Antibiotic"]
        for r in st.session_state.amr_profile
        if r["AMR Classification"] == "Susceptible"
    ]

    st.markdown("### Current Profile Interpretation")

    if resistant_drugs:
        st.error(
            "Resistance detected in the prototype profile for: "
            + ", ".join(resistant_drugs)
        )

    if susceptible_drugs:
        st.success(
            "Susceptibility detected in the prototype profile for: "
            + ", ".join(susceptible_drugs)
        )

    st.markdown("### Potential Antimicrobial Options for Review")

    if susceptible_drugs:
        st.write(
            "The following agents are currently classified as susceptible "
            "by the prototype sensor model and may be prioritized for "
            "laboratory/clinical review:"
        )
        for drug in susceptible_drugs:
            st.write(f"• {drug}")
    else:
        st.write(
            "No antibiotic in the current entered panel is classified as "
            "Susceptible by the prototype model."
        )

    st.warning(
        "Final antimicrobial selection must be based on validated AST, "
        "organism identification, infection site, patient factors, "
        "local guidelines, and clinician/laboratory review."
    )

# ==========================================================
# 10. PHAGE THERAPY CANDIDATE MODULE
# ==========================================================
st.markdown("---")
st.header("🦠 10. Phage Therapy Candidate Search")

st.info(
    "The prototype can surface database records associated with the "
    "identified host. These are research candidates for further evaluation, "
    "not automatically clinically suitable phages."
)

if organism == "Escherichia coli":

    phage_file = (
        DATA_DIR / "phage" / "processed"
        / "NCBI_Ecoli_phage_Master.csv"
    )

    if phage_file.exists():
        try:
            phage_df = pd.read_csv(phage_file)

            if "host_name" in phage_df.columns:
                matches = phage_df[
                    phage_df["host_name"]
                    .astype(str)
                    .str.contains(
                        "Escherichia coli",
                        case=False,
                        na=False
                    )
                ].copy()

                st.write(
                    f"Host-associated NCBI Virus records found: **{len(matches)}**"
                )

                display_cols = [
                    c for c in
                    ["accession", "virus_name", "host_name",
                     "completeness", "length", "release_date"]
                    if c in matches.columns
                ]

                if display_cols:
                    st.dataframe(
                        matches[display_cols].head(20),
                        use_container_width=True,
                        hide_index=True
                    )

                st.caption(
                    "NCBI Virus host association does not by itself establish "
                    "lytic activity, therapeutic suitability, or clinical efficacy."
                )

        except Exception as exc:
            st.warning(f"Could not read the NCBI Virus dataset: {exc}")

elif organism == "Acinetobacter spp.":

    st.info(
        "Acinetobacter-specific phage candidate curation can be added by "
        "linking host-filtered records from the phage reference databases."
    )

else:
    st.info("Select an organism to activate host-specific phage candidate search.")

# ==========================================================
# 11. DATABASE STATUS
# ==========================================================
st.markdown("---")
st.header("🗄️ 11. AMR-PULSE Reference Database Status")

status_df = database_status()

st.dataframe(
    status_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Reference databases provide supporting AMR/phage knowledge. "
    "They do not replace patient/isolate-specific susceptibility testing."
)

# ==========================================================
# 12. SENSOR HISTORY
# ==========================================================
st.markdown("---")
st.header("📊 12. Sensor Result History")

if st.session_state.sensor_results:
    history_df = pd.DataFrame(st.session_state.sensor_results)

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = history_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Export Sensor Results CSV",
        data=csv_data,
        file_name="AMR_PULSE_sensor_results.csv",
        mime="text/csv"
    )
else:
    st.info("No sensor results recorded in this session.")

# ==========================================================
# Footer
# ==========================================================
st.markdown("---")
st.caption(
    "AMR-PULSE prototype | Research / hackathon demonstration | "
    "Not for clinical diagnosis or treatment decisions."
)
