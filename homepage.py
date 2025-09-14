# homepage.py
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re

# ===============================
# FEATURE 1: View Grades
# ===============================
def view_grades():
    def extract_results(pdf_file, index_df):
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        pdf_text = ""
        for page in doc:
            pdf_text += page.get_text()

        results_pattern = r"([A-Za-z0-9]+)\s+(A\+|A-|A|B\+|B-|B|C\+|C-|C|D|I)"
        matches = re.findall(results_pattern, pdf_text)

        if not matches:
            st.error("⚠️ No results found in the PDF.")
            return pd.DataFrame()

        grade_order = {
            "A+": 1, "A": 2, "A-": 3,
            "B+": 4, "B": 5, "B-": 6,
            "C+": 7, "C": 8, "C-": 9,
            "D": 10, "I": 11
        }

        results = []
        for index, grade in matches:
            name = index_df.loc[index_df['IndexNumber'] == index, 'Name'].values
            if len(name) == 0:
                continue
            results.append({"Name": name[0], "Result": grade})

        results_df = pd.DataFrame(results)
        if results_df.empty:
            st.warning("⚠️ No valid results matched with index.csv")
            return results_df

        results_df["GradeOrder"] = results_df["Result"].map(grade_order)
        results_df = results_df.sort_values(by="GradeOrder").drop(columns=["GradeOrder"])
        return results_df

    st.title("📄 View Grades")
    index_file = st.file_uploader("Upload index.csv", type="csv", key="vg_index")
    if index_file is not None:
        index_df = pd.read_csv(index_file)
        st.write("✅ Index File Preview")
        st.dataframe(index_df)

        pdf_file = st.file_uploader("Upload Results PDF", type="pdf", key="vg_pdf")
        if pdf_file is not None:
            st.write("⏳ Processing results...")
            results_df = extract_results(pdf_file, index_df)
            if not results_df.empty:
                st.subheader("📑 Sorted Results")
                st.dataframe(results_df)

# ===============================
# FEATURE 2: GPA Calculator
# ===============================
def gpa_calculator():
    grade_points = {
        "A+": 4.0, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D": 1.0, "I": 0.0
    }

    def extract_results(pdf_bytes, module_name):
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pdf_text = ""
        for page in doc:
            pdf_text += page.get_text("text")

        pattern = r"([0-9A-Za-z]+)\s*\|?\s*(A\+|A-|A|B\+|B-|B|C\+|C-|C|D|I)"
        matches = re.findall(pattern, pdf_text)

        if not matches:
            st.warning(f"No results found in {module_name}")
            return pd.DataFrame(columns=["IndexNumber", module_name])

        return pd.DataFrame(matches, columns=["IndexNumber", module_name])

    st.title("📊 GPA Calculator")

    index_file = st.file_uploader("Upload index.csv", type="csv", key="gpa_index")
    if not index_file:
        st.stop()

    index_df = pd.read_csv(index_file)
    index_df.columns = index_df.columns.str.strip()

    if "IndexNumber" not in index_df.columns or "Name" not in index_df.columns:
        st.error("❌ index.csv must have 'IndexNumber' and 'Name'")
        st.stop()

    st.subheader("✅ Index File Preview")
    st.dataframe(index_df.head())

    num_modules = st.number_input("Enter number of modules", min_value=1, max_value=20, step=1)

    module_info = []
    for i in range(num_modules):
        st.subheader(f"📘 Module {i+1}")
        module_name = st.text_input(f"Module {i+1} Name", key=f"gpa_name_{i}")
        credit = st.number_input(
            f"Credit for {module_name if module_name else f'Module {i+1}'}",
            min_value=0.5, max_value=10.0, step=0.5, key=f"gpa_credit_{i}"
        )
        pdf_file = st.file_uploader(
            f"Results PDF for {module_name if module_name else f'Module {i+1}'}",
            type="pdf", key=f"gpa_pdf_{i}"
        )
        if module_name and credit and pdf_file:
            module_info.append((module_name, credit, pdf_file))

    if len(module_info) == num_modules:
        all_results = index_df.copy()
        module_credits = {}

        for module_name, credit, pdf_file in module_info:
            pdf_bytes = pdf_file.getvalue()
            results_df = extract_results(pdf_bytes, module_name)
            st.write(f"📑 Extracted Results for {module_name}:")
            st.dataframe(results_df)
            all_results = all_results.merge(results_df, on="IndexNumber", how="left")
            module_credits[module_name] = credit

        st.subheader("📑 Combined Results Table")
        st.dataframe(all_results)

        if st.button("Calculate GPA"):
            gpa_data = []
            for _, row in all_results.iterrows():
                total_weighted, total_credits = 0, 0
                for module_name, credit in module_credits.items():
                    grade = row.get(module_name, None)
                    if grade in grade_points:
                        total_weighted += grade_points[grade] * credit
                        total_credits += credit
                gpa = total_weighted / total_credits if total_credits > 0 else 0
                gpa_data.append({
                    "IndexNumber": row["IndexNumber"],
                    "Name": row["Name"],
                    "GPA": round(gpa, 2)
                })

            gpa_df = pd.DataFrame(gpa_data).sort_values(by="GPA", ascending=False).reset_index(drop=True)
            st.subheader("🏆 GPA Leaderboard")
            st.dataframe(gpa_df)

            st.download_button(
                label="⬇️ Download GPA Results (CSV)",
                data=gpa_df.to_csv(index=False).encode("utf-8"),
                file_name="gpa_results.csv",
                mime="text/csv"
            )

# ===============================
# FEATURE 3: Personalized Profile
# ===============================
def personalized_profile():
    st.title("👤 Personalized Academic Profile")

    combined_file = st.file_uploader("Upload Combined Results CSV", type="csv", key="pp_combined")
    gpa_file = st.file_uploader("Upload GPA Results CSV", type="csv", key="pp_gpa")

    if not combined_file or not gpa_file:
        st.stop()

    combined_df = pd.read_csv(combined_file)
    gpa_df = pd.read_csv(gpa_file)

    st.subheader("✅ Uploaded Data Previews")
    st.write("Combined Results:")
    st.dataframe(combined_df.head())
    st.write("GPA Results:")
    st.dataframe(gpa_df.head())

    index_number = st.text_input("Enter your Index Number:", key="pp_index")

    if index_number:
        if index_number not in combined_df["IndexNumber"].values:
            st.error("❌ Index Number not found!")
            return

        student_row = combined_df[combined_df["IndexNumber"] == index_number].iloc[0]
        gpa_row = gpa_df[gpa_df["IndexNumber"] == index_number].iloc[0]

        st.markdown('<div class="profile-card" style="display:flex;gap:20px;margin:20px 0;">', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="card" style="flex:1;background:#fff;padding:20px;border-radius:15px;box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                <h3>👤 Name</h3>
                <p>{student_row['Name']}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="card" style="flex:1;background:#fff;padding:20px;border-radius:15px;box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                <h3>📊 GPA</h3>
                <p>{gpa_row['GPA']}</p>
            </div>
        """, unsafe_allow_html=True)

        rank = gpa_df[gpa_df["IndexNumber"] == index_number].index[0] + 1
        total_students = len(gpa_df)
        st.markdown(f"""
            <div class="card" style="flex:1;background:#fff;padding:20px;border-radius:15px;box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                <h3>🏆 Rank</h3>
                <p>{rank} / {total_students}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.write("### 📘 Module Grades")
        grade_cols = [col for col in combined_df.columns if col not in ["IndexNumber", "Name"]]
        grades_table = pd.DataFrame({
            "Module": grade_cols,
            "Grade": [student_row[col] for col in grade_cols]
        })
        st.dataframe(grades_table, use_container_width=True)

# ===============================
# FEATURE 4: Chatbot
# ===============================
def chatbot():
    st.title("🤖 Grade Insights Chatbot")

    combined_file = st.file_uploader("Upload Combined Results CSV", type="csv", key="cb_combined")
    gpa_file = st.file_uploader("Upload GPA Results CSV", type="csv", key="cb_gpa")

    if not combined_file or not gpa_file:
        st.info("Upload both combined results and GPA CSV files to start the chatbot.")
        st.stop()

    combined_df = pd.read_csv(combined_file)
    gpa_df = pd.read_csv(gpa_file)

    index_number = st.text_input("Enter your Index Number:", key="cb_index")
    if not index_number:
        st.stop()

    if index_number not in combined_df["IndexNumber"].values:
        st.error("Index Number not found!")
        st.stop()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def generate_response(user_input):
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

    user_input = st.text_input("Ask a question:", key="cb_user_input")
    send_button = st.button("Send", key="cb_send")

    if send_button and user_input.strip() != "":
        response = generate_response(user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", response))

    for sender, message in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"<p style='text-align: right; color: blue;'>💬 {message}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='text-align: left; color: green;'>🤖 {message}</p>", unsafe_allow_html=True)

# ===============================
# MAIN HOMEPAGE WITH CARDS
# ===============================
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
        .chatbot { background: linear-gradient(135deg, #ff5f6d, #ffc371); }
        </style>
    """, unsafe_allow_html=True)

    st.title("🎓 Student Result System")
    st.write("### Select a Feature")

    if 'selected_feature' not in st.session_state:
        st.session_state.selected_feature = None

    features = {
        "View Grades": ("view-grades", view_grades),
        "GPA Calculator": ("gpa-calc", gpa_calculator),
        "Personalized Profile": ("profile", personalized_profile),
        "Chatbot": ("chatbot", chatbot)
    }

    for feature_name, (css_class, func) in features.items():
        if st.button(feature_name, key=feature_name):
            st.session_state.selected_feature = feature_name

    if st.session_state.selected_feature:
        features[st.session_state.selected_feature][1]()
    else:
        st.info("👆 Click on a card above to get started")

if __name__ == "__main__":
    main()
