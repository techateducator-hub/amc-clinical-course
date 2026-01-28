import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. EDIT THIS SECTION ONLY (PASTE YOUR NEW TOPIC HERE)
# ==========================================

TOPIC_SCENARIO = """
**Patient:** Sarah, 28yo female
**Setting:** GP Clinic
**Complaint:** Fatigue
"""

TOPIC_TASKS = """
1. Take a focused history.
2. Explain the likely diagnosis.
3. Counsel on management.
"""

TOPIC_RUBRIC = """
**Correct Diagnosis:** Iron Deficiency Anemia.
**Critical Error:** Failing to ask about heavy periods or diet.
**Key Points:**
* Identify microcytic anemia features.
* Ask about vegetarianism.
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
        if st.button("Grade My Audio"):
            with st.spinner('AI is analyzing your voice...'):
                try:
                    prompt = f"""
                    You are an AMC Examiner.
                    Case Scenario: {TOPIC_SCENARIO}
                    Tasks: {TOPIC_TASKS}
                    Official Answer Key: {TOPIC_RUBRIC}
                    
                    INSTRUCTIONS:
                    Listen to the student's audio.
                    1. Did they cover the critical points in the Answer Key?
                    2. Did they make any critical errors?
                    3. Give a PASS or FAIL verdict.
                    """
                    response = model.generate_content([prompt, {"mime_type": "audio/wav", "data": audio_value.read()}])
                    st.success("Grading Complete")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error grading audio: {e}")

# E. The Hidden Rubric (Clickable Reveal)
st.markdown("---")
st.write("### Review")

# This 'st.expander' line creates the hidden clickable box
with st.expander("👁️ Click to Reveal Official Rubric & Answer"):
    st.markdown("### Official Examiner Guide")
    st.markdown(TOPIC_RUBRIC)
    st.info("Tip: Compare this rubric with the AI feedback above to see where you can improve.")
