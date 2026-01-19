import streamlit as st
import google.generativeai as genai

# 1. SETUP
# This connects to the "Brain" using the key you will provide in Step 3
api_key = st.secrets["AIzaSyBGGHpYggPJqQiod2-c7HJn_oY6HqAnFBU"] 
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. THE PAGE LAYOUT
st.set_page_config(page_title="AMC Clinical Exam Trainer", layout="wide")

st.title("AMC Clinical Exam Simulation")
st.markdown("---")

# 3. INPUT THE CASE (You paste the AI generated case here)
# In a real app, you could load these from a file.
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Scenario & Tasks")
    st.info("""
    **Setting:** General Practice
    **Patient:** Sarah Jenkins, 28yo female
    **Complaint:** Fatigue
    """)
    
    st.write("**Tasks:**")
    st.write("i. Take a focused history.")
    st.write("ii. Explain the likely diagnosis.")
    st.write("iii. Counsel on management.")

    st.markdown("---")
    st.subheader("3. Reference Dialogue")
    with st.expander("View Sample Doctor/Patient Interaction"):
        st.write("""
        **Dr:** "Hello Sarah, I see you're feeling tired. Tell me more about that?"
        **Pt:** "It's been months..."
        *(Paste the AI generated dialogue here)*
        """)

# 4. THE INTERACTIVE PART
with col2:
    st.header("4. Perform Your Tasks")
    
    # Task 1 Recorder
    st.subheader("Task i: History Taking")
    user_input_1 = st.text_area("Type what you would say (or use Dictation on your phone):", key="task1")
    
    # Task 2 Recorder
    st.subheader("Task ii & iii: Diagnosis & Management")
    user_input_2 = st.text_area("Type your explanation:", key="task2")

    if st.button("Submit for Assessment"):
        if user_input_1 or user_input_2:
            with st.spinner('Analyzing your response against AMC Rubrics...'):
                # This sends your answer to the AI to be graded
                prompt = f"""
                You are an AMC Examiner. 
                Task 1 Answer: {user_input_1}
                Task 2 Answer: {user_input_2}
                
                Critique this student based on Australian Medical Council standards. 
                Be strict. Did they ask open-ended questions? Did they show empathy?
                """
                response = model.generate_content(prompt)
                st.success("Analysis Complete")
                st.write(response.text)
        else:
            st.warning("Please enter your response first.")

# 5. THE HIDDEN RUBRIC
st.markdown("---")
with st.expander("Click to Reveal Official Rubric & Answer"):
    st.error("Only open this AFTER you have attempted the case!")
    st.markdown("""
    **Critical Errors:**
    * Failure to ask about pregnancy.
    * Failure to assess for depression.
    
    **Correct Diagnosis:** Iron Deficiency Anemia secondary to menorrhagia.
    """)
