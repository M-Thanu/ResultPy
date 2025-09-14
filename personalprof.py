import streamlit as st
import pandas as pd

def app():

    def main():
        st.markdown("""
            <style>
            body {
                background: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
            }
            .profile-card {
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 20px;
                margin: 20px 0;
            }
            .card {
                flex: 1;
                min-width: 200px;
                background: white;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                text-align: center;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            }
            .card h3 {
                margin: 0;
                font-size: 22px;
                color: #333;
            }
            .card p {
                font-size: 18px;
                font-weight: 600;
                margin-top: 10px;
                color: #555;
            }
            .grades-table {
                margin-top: 20px;
            }
            </style>
        """, unsafe_allow_html=True)

        st.title("👤 Personalized Academic Profile")

        # Upload combined results
        combined_file = st.file_uploader("Upload Combined Results CSV", type="csv")
        gpa_file = st.file_uploader("Upload GPA Results CSV", type="csv")

        if not combined_file or not gpa_file:
            st.stop()

        combined_df = pd.read_csv(combined_file)
        gpa_df = pd.read_csv(gpa_file)

        st.subheader("✅ Uploaded Data Previews")
        st.write("Combined Results:")
        st.dataframe(combined_df.head())
        st.write("GPA Results:")
        st.dataframe(gpa_df.head())

        # User input
        index_number = st.text_input("Enter your Index Number:")

        if index_number:
            if index_number not in combined_df["IndexNumber"].values:
                st.error("Index Number not found!")
                return

            student_row = combined_df[combined_df["IndexNumber"] == index_number].iloc[0]
            gpa_row = gpa_df[gpa_df["IndexNumber"] == index_number].iloc[0]

            # Horizontal cards for Name, GPA, Rank
            st.markdown('<div class="profile-card">', unsafe_allow_html=True)

            st.markdown(f"""
                <div class="card">
                    <h3>👤 Name</h3>
                    <p>{student_row['Name']}</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="card">
                    <h3>📊 GPA</h3>
                    <p>{gpa_row['GPA']}</p>
                </div>
            """, unsafe_allow_html=True)

            rank = gpa_df[gpa_df["IndexNumber"] == index_number].index[0] + 1
            total_students = len(gpa_df)
            st.markdown(f"""
                <div class="card">
                    <h3>🏆 Rank</h3>
                    <p>{rank} / {total_students}</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Grades Table
            st.write("### 📘 Module Grades")
            grade_cols = [col for col in combined_df.columns if col not in ["IndexNumber", "Name"]]
            grades_table = pd.DataFrame({
                "Module": grade_cols,
                "Grade": [student_row[col] for col in grade_cols]
            })
            st.dataframe(grades_table, use_container_width=True)

    # -----------------------------
    if __name__ == "__main__":
        main()
