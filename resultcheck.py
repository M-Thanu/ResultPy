import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re

def app():
    def extract_results(pdf_file, index_df):
        # Read PDF content
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        pdf_text = ""
        for page in doc:
            pdf_text += page.get_text()

        # Extract index numbers and grades
        results_pattern = r"([A-Za-z0-9]+)\s+(A\+|A\-|A|B\+|B\-|B|C\+|C\-|C|D|I)"
        matches = re.findall(results_pattern, pdf_text)

        if not matches:
            st.error("No results found in the PDF. Check the format and regex pattern.")
            return pd.DataFrame()

        # Custom grade sorting order
        grade_order = {
            "A+": 1, "A": 2, "A-": 3,
            "B+": 4, "B": 5, "B-": 6,
            "C+": 7, "C": 8, "C-": 9,
            "D": 10, "I": 11
        }

        # Map results to names
        results = []
        for index, grade in matches:
            name = index_df.loc[index_df['IndexNumber'] == index, 'Name'].values
            if len(name) == 0:
                continue  # skip unknown indices
            results.append({"Name": name[0], "Result": grade})

        # Build DataFrame
        results_df = pd.DataFrame(results)
        if results_df.empty:
            st.warning("No valid results matched the index numbers in the database.")
            return results_df

        # Apply custom grade sort
        results_df["GradeOrder"] = results_df["Result"].map(grade_order)
        results_df = results_df.sort_values(by="GradeOrder").drop(columns=["GradeOrder"])
        return results_df

    # --- Streamlit UI ---
    st.title("📄 View Grades")
    st.write("Upload the results PDF and view results in a sorted table.")

    # Upload index.csv
    index_file = st.file_uploader("Upload index.csv", type="csv")
    if index_file is not None:
        index_df = pd.read_csv(index_file)
        st.write("Pre-fed data:")
        st.dataframe(index_df)

        # Upload PDF file
        pdf_file = st.file_uploader("Upload Results PDF", type="pdf")
        if pdf_file is not None:
            st.write("Processing results...")
            results_df = extract_results(pdf_file, index_df)
            if not results_df.empty:
                st.write("Results (sorted in descending order):")
                st.dataframe(results_df)
