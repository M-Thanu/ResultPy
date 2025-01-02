import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re

# Define the descending order of grades
grade_order = {
    "A+": 1,
    "A": 2,
    "A-": 3,
    "B+": 4,
    "B": 5,
    "B-": 6,
    "C+": 7,
    "C": 8,
    "C-": 9,
    "D": 10,
    "I": 11,
}

def extract_results(pdf_file, index_df):
    # Read PDF content
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    pdf_text = ""
    for page in doc:
        pdf_text += page.get_text()

    # Debug: Display the extracted text from the PDF
    #st.write("Extracted PDF Text:")
    #st.text(pdf_text)

    # Extract index numbers and grades
    results_pattern = r"([A-Za-z0-9]+)\s+([A\+|A|A\-|B\+|B|B\-|C\+|C|C\-|D|I])"
    matches = re.findall(results_pattern, pdf_text)

    if not matches:
        st.error("No results found in the PDF. Check the format and regex pattern.")
        return pd.DataFrame()

    # Map results to names
    results = []
    for index, grade in matches:
        name = index_df.loc[index_df['IndexNumber'] == index, 'Name'].values
        if len(name) == 0:
            # Skip unknown results by continuing to the next iteration
            continue
        else:
            name = name[0]
        results.append({"Name": name, "Result": grade})

    # Sort results based on grades
    results_df = pd.DataFrame(results)
    if results_df.empty:
        st.warning("No valid results matched the index numbers in the database.")
        return results_df

    results_df["GradeOrder"] = results_df["Result"].map(grade_order)
    results_df = results_df.sort_values(by="GradeOrder").drop(columns=["GradeOrder"])
    return results_df




# Streamlit app
def main():
    st.title("Results Checking System")
    st.write("Upload the results PDF and view results in a sorted table.")

    # Upload index.csv
    index_file = st.file_uploader("Upload index.csv", type="csv")
    if index_file is not None:
        # Load the CSV file
        index_df = pd.read_csv(index_file)
        st.write("Pre-fed data:")
        st.dataframe(index_df)

        # Upload PDF file
        pdf_file = st.file_uploader("Upload Results PDF", type="pdf")
        if pdf_file is not None:
            # Process and display results
            st.write("Processing results...")
            results_df = extract_results(pdf_file, index_df)
            st.write("Results (sorted in descending order):")
            st.dataframe(results_df)

# Run the Streamlit app
if __name__ == "__main__":
    main()
