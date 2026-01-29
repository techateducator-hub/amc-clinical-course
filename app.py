import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. EDIT THIS SECTION ONLY (YOUR CONTENT)
# ==========================================

TOPIC_SCENARIO = """
**Patient:** James, 68-year-old male.
**Setting:** Emergency Department.
**Presenting Complaint:** Pain, weakness, and "pins and needles" in the right hand after a fall.

**Situation:**
James was brought in after falling from a tree. He states he tried to grab a branch on the way down to break his fall. He is hemodynamically stable.
"""

TOPIC_TASKS = """
1. **General Inspection:** Perform a focused inspection of the hand and arm, noting specific deformities.
2. **Neurological Exam:** Assess Motor and Sensory function using a myotomal/dermatomal approach (adapting to patient's pain).
3. **Diagnosis:** Explain the diagnosis of Lower Brachial Plexus Injury to the patient, detailing the C8/T1 involvement.
"""

TOPIC_RUBRIC = """
**DIAGNOSIS:** Lower Brachial Plexus Injury (Klumpke’s Palsy).

**CRITICAL ERRORS (FAIL CRITERIA):**
* **Forcing Passive Movement:** Attempting to force joints when the patient refuses due to pain.
* **Incorrect Diagnosis:** Diagnosing simple Ulnar Nerve palsy instead of Brachial Plexus injury.
* **Missing T1 Involvement:** Failing to check sensation on the inner elbow (T1 dermatome).

**KEY FINDINGS (To be elicited):**
* **Inspection:** Full Claw Hand (all fingers curled), patient holds arm still.
* **Motor:** Patient refuses active movement due to pain.
* **Sensory:** Numbness in Little Finger (C8) AND Inner Elbow (T1). Normal sensation in Thumb (C6) and Middle Finger (C7).

**PATIENT SCRIPT (How the patient acted):**
* **Attitude:** In pain, guarding the arm.
* **Reaction:** If doctor tries to force movement, patient cries out and pulls away.
* **History:** "I grabbed a branch to stop falling and it yanked my arm." (Hyper-abduction mechanism).
"""

# ==========================================
# 2. DO NOT TOUCH THE CODE BELOW
# ==========================================

# A. Setup Google AI
try:
    api_key = st.secrets["GEMINI_API_KEY"] 
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Error: API Key is missing. Please set it in Streamlit Secrets.")

# B. Page Setup
st.set_page_config(page_title="AMC Clinical Exam", layout="wide")
st.title("AMC Clinical Exam Simulation")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# C. Left Column: The Case
with col1:
    st.header("1. Scenario")
    st.info(TOPIC_SCENARIO)  
    
    st.subheader("Tasks")
    st.markdown(TOPIC_TASKS) 

# D. Right Column: Audio Recorder & Grading
with col2:
    st.header("2. Perform Task (Audio)")
    st.write("Record your answer to the tasks on the left.")
    
    # The Audio Input
    audio_value = st.audio_input("Record your answer")

    if audio_value:
        st.audio(audio_value)
        if st.button("Transcribe & Grade My Audio"):
            with st.spinner('AI is transcribing and analyzing...'):
                try:
                    # We send the SCENARIO + TASKS + RUBRIC (Context) to the AI
                    prompt = f"""
                    You are an expert AMC Examiner.
                    
                    --- CASE DATA ---
                    SCENARIO: {TOPIC_SCENARIO}
                    TASKS: {TOPIC_TASKS}
                    RUBRIC/ANSWER KEY: {TOPIC_RUBRIC}
                    
                    --- INSTRUCTIONS ---
                    Listen to the student's audio recording.
                    
                    STEP 1: TRANSCRIPT
                    Write down a verbatim transcript of exactly what the student said.
                    Label this section "### 📝 Audio Transcript".
                    
                    STEP 2: EVALUATION
                    Compare the transcript against the Rubric.
                    1. **Safety Check:** Did they force movement?
                    2. **Clinical Check:** Did they find the C8/T1 sensory loss?
                    3. **Diagnosis:** Did they identify Klumpke's Palsy?
                    Label this section "### 👨‍⚕️ Examiner Feedback".
                    
                    STEP 3: VERDICT
                    Give a final PASS or FAIL.
                    """
                    
                    response = model.generate_content([
                        prompt, 
                        {
                            "mime_type": "audio/wav", 
                            "data": audio_value.read()
                        }
                    ])
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error processing audio: {e}")

# E. The Hidden Rubric (Clickable Reveal)
st.markdown("---")
st.write("### Review")

# This 'st.expander' line creates the hidden clickable box
with st.expander("👁️ Click to Reveal Official Rubric & Diagnosis"):
    st.markdown("### Official Examiner Guide")
    st.markdown(TOPIC_RUBRIC)
    st.info("Tip: Compare the 'Critical Errors' above with the AI feedback.")
