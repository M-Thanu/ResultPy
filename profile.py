import streamlit as st
import pandas as pd

# Example grade points mapping
grade_points = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D": 1.0, "I": 0.0
}

def personalized_profile(all_results, module_credits):
    st.title("👤 Personalized Profile")

    index_number = st.text_input("Enter your Index Number:")

    if index_number:
        # Check if index exists
        if index_number not in all_results["IndexNumber"].values:
            st.error("Index Number not found!")
            return

        # Fetch student row
        student_row = all_results[all_results["IndexNumber"] == index_number].iloc[0]

        st.subheader(f"Name: {student_row['Name']}")
        st.write("### Module Grades")
        
        # Display grades table
        grades_table = pd.DataFrame({
            "Module": list(module_credits.keys()),
            "Grade": [student_row.get(mod, "N/A") for mod in module_credits.keys()]
        })
        st.dataframe(grades_table)

        # Calculate GPA
        total_weighted, total_credits = 0, 0
        for mod, credit in module_credits.items():
            grade = student_row.get(mod, None)
            if grade in grade_points:
                total_weighted += grade_points[grade] * credit
                total_credits += credit
        gpa = total_weighted / total_credits if total_credits > 0 else 0
        st.write(f"### GPA: {round(gpa,2)}")

        # Calculate rank
        gpa_list = []
        for _, row in all_results.iterrows():
            tw, tc = 0, 0
            for mod, credit in module_credits.items():
                grade = row.get(mod, None)
                if grade in grade_points:
                    tw += grade_points[grade] * credit
                    tc += credit
            gpa_list.append(tw / tc if tc > 0 else 0)
        all_results["GPA"] = gpa_list
        all_results_sorted = all_results.sort_values(by="GPA", ascending=False).reset_index(drop=True)
        rank = all_results_sorted[all_results_sorted["IndexNumber"] == index_number].index[0] + 1
        st.write(f"### Rank in Batch: {rank} / {len(all_results_sorted)}")
