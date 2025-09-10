import streamlit as st
import pandas as pd
import fitz  # PyMuPDF for text PDFs
from pdf2image import convert_from_bytes  # For OCR
import pytesseract
import re

# -----------------------------
# Grade to grade-point mapping
grade_points = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D": 1.0, "I": 0.0
}

# -----------------------------
# Extract text from PDF (text-based or scanned)
def extract_pdf_text(pdf_file):
    """Return list of lines from PDF using text extraction or OCR."""
    lines = []

    # Try text extraction first
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            lines.extend(text.split("\n"))

    # If no text found → use OCR
    if not lines:
        pdf_file.seek(0)  # reset file pointer
        images = convert_from_bytes(pdf_file.read())
        for img in images:
            text = pytesseract.image_to_string(img)
            lines.extend(text.split("\n"))

    # Clean lines
    lines = [line.strip() for line in lines if line.strip()]
    return lines

# -----------------------------
# Extract IndexNumber and Grade from lines
def parse_results(lines):
    index_list, grade_list = [], []

    grades_set = grade_points.keys()
    for line in lines:
        # Search for any grade in the line
        for g in grades_set:
            if g in line:
                # Try to find a number before the grade
                index_match = re.search(r'\d+', line)
                if index_match:
                    index_list.append(index_match.group())
                    grade_list.append(g)
                break  # only take first grade per line

    df = pd.DataFrame({
        "IndexNumber": index_list,
        "Grade": grade_list
    })
    return df

# -----------------------------
# Streamlit App
def main():
    st.title("📊 GPA Calculator (PDF OCR Compatible)")

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

    # Step 2: Get module names and credits
    num_modules = st.number_input("Enter number of modules", min_value=1, max_value=20, step=1)
    module_list = []

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
        if module_name and credit:
            module_list.append({"Module": module_name, "Credit": credit, "PDF": pdf_file})

    # Step 3: Show module summary
    if module_list:
        st.subheader("📑 Module Summary Table")
        module_df = pd.DataFrame([{**m, "PDF Uploaded": bool(m["PDF"])} for m in module_list])
        st.dataframe(module_df[["Module", "Credit", "PDF Uploaded"]])

    # Step 4: Process PDFs and show combined results
    if all(m["PDF"] for m in module_list) and st.button("Process PDFs & Show Results"):
        all_results = index_df.copy()
        module_credits = {}

        for m in module_list:
            module_name = m["Module"]
            credit = m["Credit"]
            pdf_file = m["PDF"]

            # Extract text & parse grades
            lines = extract_pdf_text(pdf_file)
            results_df = parse_results(lines)
            results_df.rename(columns={"Grade": module_name}, inplace=True)

            st.write(f"📑 Extracted Results for {module_name}")
            st.dataframe(results_df)

            # Merge with index_df
            all_results = all_results.merge(results_df, on="IndexNumber", how="left")
            module_credits[module_name] = credit

        st.subheader("📊 Combined Results Table")
        st.dataframe(all_results)

        # Step 5: Calculate GPA
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

# -----------------------------
if __name__ == "__main__":
    main()
