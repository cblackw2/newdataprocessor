# Installation Instructions:
# Ensure you have these packages installed:
# pip install streamlit pandas openpyxl

import re
import streamlit as st
import pandas as pd

# Set the title of the Streamlit web app
st.title("Data Flow Visualization App (Mermaid Syntax)")

# Sidebar instructions
st.sidebar.header("Upload Excel File")
st.sidebar.write("Upload an Excel (.xlsx) file containing the data flow information.")

# File uploader widget
uploaded_file = st.sidebar.file_uploader("Choose an Excel file", type=["xlsx"])

# List of expected columns for dynamic mode
expected_columns = [
    "Use Case/Scenario",
    "Functional Area",
    "DCL",
    "Where data is sourced from",
    "Platform used to aggregate data",
    "Platform used to analyze data",
    "Platform used to publish curated data",
    "Compliance"
]

def sanitize_label(label):
    """
    Aggressively sanitize the node label:
      - Convert to string.
      - Strip whitespace and newline characters.
      - Replace double quotes with single quotes.
      - Replace slashes ("/") with dashes ("-").
      - Replace spaces with underscores.
      - Remove all characters except letters, numbers, underscores, and dashes.
    """
    if not isinstance(label, str):
        label = str(label)
    label = label.strip().replace("\n", " ").replace('"', "'").replace("/", "-")
    label = label.replace(" ", "_")
    label = re.sub(r'[^\w\-]', '', label)
    return label

def process_data(file):
    """
    Reads the uploaded Excel file into a DataFrame,
    verifies that all expected columns are present, and fills missing values.
    """
    try:
        df = pd.read_excel(file)
        missing_cols = [col for col in expected_columns if col not in df.columns]
        if missing_cols:
            st.error(f"Missing expected columns: {', '.join(missing_cols)}")
            return None
        df.fillna("N/A", inplace=True)
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

def generate_dynamic_mermaid_definition(df):
    """
    Generates a Mermaid diagram definition from the Excel data.
    The intended flow is:
      "Where data is sourced from" --> "Platform used to aggregate data" -->
      "Platform used to analyze data" --> "Platform used to publish curated data"
      
    Each node name is sanitized (spaces replaced with underscores, etc.),
    and each edge is defined as: Node1 --> Node2;
    The diagram starts with "flowchart LR;".
    """
    edges = set()
    for idx, row in df.iterrows():
        source = sanitize_label(row["Where data is sourced from"])
        agg = sanitize_label(row["Platform used to aggregate data"])
        analysis = sanitize_label(row["Platform used to analyze data"])
        publish = sanitize_label(row["Platform used to publish curated data"])
        edges.add(f"{source} --> {agg};")
        edges.add(f"{agg} --> {analysis};")
        edges.add(f"{analysis} --> {publish};")
    
    lines = [line.strip() for line in sorted(edges)]
    mermaid_def = "flowchart LR;\n" + "\n".join(lines)
    return mermaid_def

def generate_analysis_summary(df):
    """
    Displays a summary of the unique counts of values for each key column.
    """
    st.subheader("Analysis Summary")
    st.write("Summary of key insights from the uploaded data:")
    for col in expected_columns:
        unique_values = df[col].unique()
        st.write(f"**{col}**: {len(unique_values)} unique value(s)")
    st.write("This provides a quick overview of the data diversity.")

# Main application logic
if uploaded_file is not None:
    data = process_data(uploaded_file)
    if data is not None:
        st.subheader("Data Preview")
        st.write(data.head())
        mermaid_def = generate_dynamic_mermaid_definition(data)
        st.subheader("Mermaid Syntax")
        st.code(mermaid_def, language="mermaid")
        generate_analysis_summary(data)
else:
    st.info("Please upload an Excel file to proceed.")
