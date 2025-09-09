import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re

# Grade to grade-point mapping
grade_points = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D": 1.0, "I": 0.0
}

def extract_results(pdf_bytes, module_name):
    """Extract IndexNumber and Grade from PDF (Index No. in PDF)"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pdf_text = ""
    for page in doc:
        pdf_text += page.get_text()

    # Regex for Index No. + Grade
    pattern = r"([A-Za-z0-9]+)\s+(A\+|A-|A|B\+|B-|B|C\+|C-|C|D|I)"
    matches = re.findall(pattern, pdf_text)

    if not matches:
        st.warning(f"No valid results found in PDF for {module_name}.")
        return pd.DataFrame(columns=["IndexNumber", module_name])

    index_list = []
    grade_list = []

    for index_no, grade in matches:
        index_list.append(index_no.strip())
        grade_list.append(grade.strip())

    df = pd.DataFrame({
        "IndexNumber": index_list,
        module_name: grade_list
    })

    return df

def main():
    st.title("📊 GPA Calculator (Dynamic Modules, PDF Input)")

    # Step 1: Upload index.csv
    index_file = st.file_uploader("Upload index.csv (must have IndexNumber, Name columns)", type="csv")
    if not index_file:
        st.stop()

    index_df = pd.read_csv(index_file)
    index_df.columns = index_df.columns.str.strip()

    if "IndexNumber" not in index_df.columns or "Name" not in index_df.columns:
        st.error("index.csv must have 'IndexNumber' and 'Name' columns.")
        st.stop()

    st.subheader("✅ Index File Preview")
    st.dataframe(index_df.head())

    # Step 2: Ask number of modules
    num_modules = st.number_input("Enter number of modules", min_value=1, max_value=20, step=1)

    module_info = []
    for i in range(num_modules):
        st.subheader(f"📘 Module {i+1}")
        module_name = st.text_input(f"Module {i+1} Name", key=f"name_{i}")
        credit = st.number_input(
            f"Credit for {module_name if module_name else f'Module {i+1}'}",
            min_value=0.5, max_value=10.0, step=0.5, key=f"credit_{i}"
        )
        pdf_file = st.file_uploader(
            f"Results PDF for {module_name if module_name else f'Module {i+1}'}",
            type="pdf", key=f"pdf_{i}"
        )
        if module_name and credit and pdf_file:
            module_info.append((module_name, credit, pdf_file))

    # Step 3: Process PDFs and combine results
    if len(module_info) == num_modules:
        all_results = index_df.copy()
        module_credits = {}

        for module_name, credit, pdf_file in module_info:
            pdf_bytes = pdf_file.getvalue()
            results_df = extract_results(pdf_bytes, module_name)

            st.write(f"📑 Extracted Results for {module_name}:")
            st.dataframe(results_df)

            # Merge with index_df on IndexNumber
            all_results = all_results.merge(results_df, on="IndexNumber", how="left")
            module_credits[module_name] = credit

        st.subheader("📑 Combined Results Table")
        st.dataframe(all_results)

        # Step 4: Calculate GPA
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
                label="Download GPA Results (CSV)",
                data=gpa_df.to_csv(index=False).encode("utf-8"),
                file_name="gpa_results.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
