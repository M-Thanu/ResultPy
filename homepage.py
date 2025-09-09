import streamlit as st

# -----------------------------
# Feature 1: View Grades
def view_grades():
    st.title("📄 View Grades")
    st.write("Upload results PDFs and index.csv to view sorted results.")
    # Place your existing feature 1 code here

# -----------------------------
# Feature 2: GPA Calculator
def gpa_calculator():
    st.title("📊 GPA Calculator")
    st.write("Upload results PDFs and enter module credits to calculate GPA.")
    # Place your GPA calculator code here

# -----------------------------
# Feature 3: Personalized Profile
def personalized_profile():
    st.title("👤 Personalized Profile")
    st.write("Enter your IndexNumber to see your grades, GPA, and rank.")
    # Will implement later

# -----------------------------
# Feature 4: AI Chatbot
def chatbot():
    st.title("🤖 Grade Insights Chatbot")
    st.write("Ask questions like 'What is my best module?' or 'Show top 5 students in Module X'.")
    # Will implement later

# -----------------------------
# Homepage with Horizontal Cards
def main():
    st.title("🎓 Student Result System")

    # Session state to keep track of selected feature
    if 'selected_feature' not in st.session_state:
        st.session_state.selected_feature = None

    st.write("### Select a Feature")
    cols = st.columns(4)

    features = ["View Grades", "GPA Calculator", "Personalized Profile", "Chatbot"]
    icons = ["📄", "📊", "👤", "🤖"]

    for i, col in enumerate(cols):
        if col.button(f"{icons[i]} {features[i]}", key=f"card_{i}"):
            st.session_state.selected_feature = features[i]

    # Display selected feature
    if st.session_state.selected_feature == "View Grades":
        view_grades()
    elif st.session_state.selected_feature == "GPA Calculator":
        gpa_calculator()
    elif st.session_state.selected_feature == "Personalized Profile":
        personalized_profile()
    elif st.session_state.selected_feature == "Chatbot":
        chatbot()
    else:
        st.write("Click on a card above to select a feature.")

if __name__ == "__main__":
    main()
