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
# Homepage with Stylish Cards
def main():
    st.markdown("""
        <style>
        body {
            background: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
        }
        .feature-card button {
            width: 100%;
            padding: 20px;
            margin: 15px 0;
            border: none;
            border-radius: 15px;
            color: white;
            font-size: 20px;
            font-weight: 600;
            text-align: center;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .feature-card button:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }
        .view-grades { background: linear-gradient(135deg, #667eea, #764ba2); }
        .gpa-calc { background: linear-gradient(135deg, #f7971e, #ffd200); }
        .profile { background: linear-gradient(135deg, #43cea2, #185a9d); }
        .chatbot { background: linear-gradient(135deg, #fc466b, #3f5efb); }
        </style>
    """, unsafe_allow_html=True)

    st.title("🎓 Student Result System")
    st.write("### Select a Feature")

    # Session state to keep track of selected feature
    if 'selected_feature' not in st.session_state:
        st.session_state.selected_feature = None

    # Define features with CSS classes
    features = {
        "View Grades": ("view-grades", "📄"),
        "GPA Calculator": ("gpa-calc", "📊"),
        "Personalized Profile": ("profile", "👤"),
        "Chatbot": ("chatbot", "🤖"),
    }

    # Render feature cards as styled buttons
    for feature, (css_class, icon) in features.items():
        if st.markdown(
            f"""
            <div class="feature-card">
                <form action="?feature={feature}" method="get">
                    <button class="{css_class}" type="submit">{icon} {feature}</button>
                </form>
            </div>
            """,
            unsafe_allow_html=True
        ):
            pass

    # Detect selected feature from query params
    query_params = st.experimental_get_query_params()
    if "feature" in query_params:
        st.session_state.selected_feature = query_params["feature"][0]

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
        st.info("Click on a card above to select a feature.")

if __name__ == "__main__":
    main()
