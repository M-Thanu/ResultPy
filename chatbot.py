# chatbot.py
import streamlit as st
import pandas as pd

def app():
    st.set_page_config(page_title="Grade Insights Chatbot", page_icon="🤖")
    st.title("🤖 Grade Insights Chatbot")

    # Upload CSV files
    combined_file = st.file_uploader("Upload Combined Results CSV", type="csv")
    gpa_file = st.file_uploader("Upload GPA Results CSV", type="csv")

    if not combined_file or not gpa_file:
        st.info("Upload both combined results and GPA CSV files to start the chatbot.")
        st.stop()

    combined_df = pd.read_csv(combined_file)
    gpa_df = pd.read_csv(gpa_file)

    # Input index number
    index_number = st.text_input("Enter your Index Number:")
    if not index_number:
        st.stop()

    if index_number not in combined_df["IndexNumber"].values:
        st.error("Index Number not found!")
        st.stop()

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Function to generate response
    def generate_response(user_input, combined_df, gpa_df, index_number):
        student_row = combined_df[combined_df["IndexNumber"] == index_number].iloc[0]
        gpa_row = gpa_df[gpa_df["IndexNumber"] == index_number].iloc[0]
        grade_cols = [col for col in combined_df.columns if col not in ["IndexNumber", "Name"]]

        user_input = user_input.lower()

        if "weak" in user_input or "concentrate" in user_input:
            grades = {col: student_row[col] for col in grade_cols}
            weak_modules = [mod for mod, grade in grades.items() if grade in ["D", "C-", "C", "C+"]]
            if weak_modules:
                return "You should concentrate more on: " + ", ".join(weak_modules)
            else:
                return "Great! No weak modules found."
        elif "strong" in user_input or "best" in user_input:
            grades = {col: student_row[col] for col in grade_cols}
            strong_modules = [mod for mod, grade in grades.items() if grade in ["A+", "A", "A-"]]
            if strong_modules:
                return "You performed well in: " + ", ".join(strong_modules)
            else:
                return "Keep improving! No modules with top grades yet."
        elif "top" in user_input or "first" in user_input:
            top_student = gpa_df.iloc[0]
            return f"The top student in the batch is: {top_student['Name']} with GPA {top_student['GPA']}"
        else:
            return "Sorry, I can only answer questions about your strong/weak modules or top student."

    # Chat input
    user_input = st.text_input("Ask a question:", key="user_input")
    send_button = st.button("Send")

    if send_button and user_input.strip() != "":
        response = generate_response(user_input, combined_df, gpa_df, index_number)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", response))

    # Display chat history
    for sender, message in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"<p style='text-align: right; color: blue;'>💬 {message}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='text-align: left; color: green;'>🤖 {message}</p>", unsafe_allow_html=True)


if __name__ == "__main__":
    app()
