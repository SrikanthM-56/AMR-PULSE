import streamlit as st

# ==========================================
# AMR-PULSE
# AI-Powered Rapid AMR Profiling
# ==========================================

st.set_page_config(
    page_title="AMR-PULSE",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 AMR-PULSE")
st.subheader("AI-Powered Rapid AMR Profiling & Decision Support")

st.markdown("---")

st.info(
    "Prototype decision-support system. "
    "Recommendations are for laboratory workflow demonstration "
    "and do not replace clinical judgment or laboratory guidelines."
)

# ==========================================================
# PATIENT INFORMATION
# ==========================================================

st.header("👤 Patient Information")

col1, col2, col3 = st.columns(3)

with col1:
    patient_name = st.text_input("Patient Name")

with col2:
    age = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        value=25
    )

with col3:
    sex = st.selectbox(
        "Sex",
        ["Select", "Male", "Female", "Other"]
    )

# ==========================================================
# CLINICAL INFORMATION
# ==========================================================

st.header("🩺 Clinical Information")

infection_site = st.selectbox(
    "Suspected Infection Site",
    [
        "Select",
        "Urinary Tract",
        "Respiratory Tract",
        "Bloodstream",
        "Wound / Skin",
        "Gastrointestinal",
        "Other"
    ]
)

symptoms = st.multiselect(
    "Symptoms",
    [
        "Fever",
        "Chills",
        "Cough",
        "Shortness of breath",
        "Burning urination",
        "Frequent urination",
        "Abdominal pain",
        "Diarrhea",
        "Wound discharge",
        "Other"
    ]
)

# ==========================================================
# PREVIOUS ANTIMICROBIAL EXPOSURE
# ==========================================================

st.header("💊 Previous Medication / Antibiotic History")

previous_antibiotics = st.multiselect(
    "Has the patient taken any antibiotics recently?",
    [
        "Amoxicillin",
        "Amoxicillin-Clavulanate",
        "Ceftriaxone",
        "Cefixime",
        "Ciprofloxacin",
        "Levofloxacin",
        "Azithromycin",
        "Doxycycline",
        "Piperacillin-Tazobactam",
        "Meropenem",
        "Other / Unknown",
        "No previous antibiotic"
    ]
)

if previous_antibiotics:

    st.write("Selected previous antibiotics:")

    for drug in previous_antibiotics:
        st.write("•", drug)

    st.caption(
        "Previous antibiotic exposure will be considered when "
        "prioritizing AST testing in this prototype."
    )

st.markdown("---")

# ==========================================================
# TEST RECOMMENDATION
# ==========================================================

st.header("🧪 Test Recommendation")

if st.button("🔬 Generate Recommended Tests", type="primary"):

    if not patient_name:
        st.warning("Please enter the patient name.")

    elif infection_site == "Select":
        st.warning("Please select the suspected infection site.")

    elif len(symptoms) == 0:
        st.warning("Please select at least one symptom.")

    else:

        st.success("Initial assessment completed.")

        st.subheader("Recommended Diagnostic Workflow")

        # --------------------------------------------------
        # URINARY TRACT
        # --------------------------------------------------

        if infection_site == "Urinary Tract":

            st.markdown("### 🧪 Urinary Infection")

            st.checkbox(
                "Urine routine examination / microscopy",
                value=True
            )

            st.checkbox(
                "Urine culture",
                value=True
            )

            st.checkbox(
                "Organism identification",
                value=True
            )

            st.checkbox(
                "Antimicrobial Susceptibility Testing (AST)",
                value=True
            )

        # --------------------------------------------------
        # RESPIRATORY
        # --------------------------------------------------

        elif infection_site == "Respiratory Tract":

            st.markdown("### 🫁 Respiratory Infection")

            st.checkbox(
                "Appropriate respiratory specimen testing",
                value=True
            )

            st.checkbox(
                "Bacterial culture where clinically indicated",
                value=True
            )

            st.checkbox(
                "Organism identification",
                value=True
            )

            st.checkbox(
                "Antimicrobial Susceptibility Testing (AST)",
                value=True
            )

        # --------------------------------------------------
        # BLOODSTREAM
        # --------------------------------------------------

        elif infection_site == "Bloodstream":

            st.markdown("### 🩸 Bloodstream Infection")

            st.checkbox(
                "Blood culture",
                value=True
            )

            st.checkbox(
                "Organism identification",
                value=True
            )

            st.checkbox(
                "Antimicrobial Susceptibility Testing (AST)",
                value=True
            )

        # --------------------------------------------------
        # WOUND
        # --------------------------------------------------

        elif infection_site == "Wound / Skin":

            st.markdown("### 🩹 Wound / Skin Infection")

            st.checkbox(
                "Appropriate wound specimen collection",
                value=True
            )

            st.checkbox(
                "Bacterial culture where clinically indicated",
                value=True
            )

            st.checkbox(
                "Organism identification",
                value=True
            )

            st.checkbox(
                "Antimicrobial Susceptibility Testing (AST)",
                value=True
            )

        # --------------------------------------------------
        # GASTROINTESTINAL
        # --------------------------------------------------

        elif infection_site == "Gastrointestinal":

            st.markdown("### 🦠 Gastrointestinal Infection")

            st.checkbox(
                "Appropriate stool specimen testing",
                value=True
            )

            st.checkbox(
                "Pathogen testing / culture where indicated",
                value=True
            )

            st.checkbox(
                "Organism identification",
                value=True
            )

            st.checkbox(
                "Antimicrobial Susceptibility Testing where indicated",
                value=True
            )

        else:

            st.markdown("### 🔬 Further Clinical Evaluation")

            st.write(
                "Select appropriate diagnostic testing based on "
                "clinical presentation and specimen site."
            )

        # ==================================================
        # AST PRIORITIZATION
        # ==================================================

        st.markdown("---")

        st.header("💊 AST Prioritization")

        st.write(
            "After organism identification, AMR-PULSE can prioritize "
            "a small AST panel using previous antibiotic exposure "
            "together with the identified organism and laboratory rules."
        )

        if "No previous antibiotic" in previous_antibiotics:

            st.info(
                "No previous antibiotic exposure was reported. "
                "AST selection should therefore be based primarily "
                "on the identified organism, specimen and applicable "
                "laboratory guidelines."
            )

        elif previous_antibiotics:

            st.warning(
                "Previous antibiotic exposure detected."
            )

            st.write(
                "For the prototype, previously used antibiotics "
                "can be flagged for susceptibility testing to assess "
                "whether resistance may have emerged."
            )

            st.write("### Previously Used Drugs to Consider for AST")

            for drug in previous_antibiotics:

                if drug != "Other / Unknown":

                    st.write("🔸", drug)

            st.write("### Alternative AST Candidate")

            st.info(
                "An alternative antimicrobial should be selected "
                "after organism identification according to the "
                "applicable AST guideline / laboratory panel."
            )

        else:

            st.info(
                "No antibiotic history entered."
            )

        # ==================================================
        # NEXT STEP
        # ==================================================

        st.markdown("---")

        st.header("➡️ Next Step")

        st.write(
            "1. Perform the recommended diagnostic testing."
        )

        st.write(
            "2. Enter the identified pathogen."
        )

        st.write(
            "3. AMR-PULSE will generate an AST priority panel."
        )

        st.write(
            "4. Enter the laboratory AST results."
        )

        st.write(
            "5. Generate the patient's AMR Profile."
        )

        st.write(
            "6. Update the AMR Passport."
        )

        st.warning(
            "Prototype only: final test selection, AST interpretation "
            "and treatment decisions must follow qualified laboratory "
            "and clinical guidance."
       

)

# ==========================================================
# ORGANISM IDENTIFICATION
# ==========================================================

st.markdown("---")

st.header("🦠 Organism Identification")

st.info(
    "Enter the organism identified by the diagnostic laboratory. "
    "This information will be used to determine the relevant "
    "AMR reference data and subsequent analysis."
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


# ==========================================================
# SENSOR OD DATA INPUT
# ==========================================================

if organism != "Select":

    st.markdown("---")

    st.header("🧪 AMR-PULSE Sensor Data")

    st.info(
        "Enter the optical density (OD) measurements obtained "
        "from the experimental sensor workflow. These values "
        "are stored for later AMR model analysis."
    )

    antibiotic = st.selectbox(
        "Select Antibiotic",
        [
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
        ],
        index=0
    )

    st.markdown("### 📊 OD Measurements")

    col1, col2, col3 = st.columns(3)

    with col1:
        od_1 = st.number_input(
            "Replicate 1",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.01,
            format="%.2f"
        )

    with col2:
        od_2 = st.number_input(
            "Replicate 2",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.01,
            format="%.2f"
        )

    with col3:
        od_3 = st.number_input(
            "Replicate 3",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.01,
            format="%.2f"
        )

    if st.button("💾 Record Sensor Result"):

        if antibiotic == "Select":

            st.warning(
                "Please select an antibiotic before recording "
                "the sensor result."
            )

        elif od_1 == 0.0 and od_2 == 0.0 and od_3 == 0.0:

            st.warning(
                "Please enter at least one OD measurement."
            )

        else:

            mean_od = (od_1 + od_2 + od_3) / 3

            st.success(
                f"Sensor result recorded for {antibiotic}."
            )

            st.metric(
                "Mean OD",
                f"{mean_od:.2f}"
            )

            st.caption(
                "No S/I/R classification is performed yet. "
                "The experimental OD-to-AMR model will be added "
                "after validated training data are available."
            )
    index=0
)

if organism != "Select":
    st.success(f"Organism selected: {organism}")

    st.caption(
        "Prototype organisms are currently limited to the organisms "
        "represented in the AMR-PULSE reference dataset."
    )