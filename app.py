# Installation Instructions:
# Run the following commands to install the required dependencies:
# pip install streamlit pandas networkx matplotlib openpyxl

import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Set the title of the Streamlit web app
st.title("Data Flow Visualization App")

# Sidebar instructions
st.sidebar.header("Upload Excel File")
st.sidebar.write("Upload an Excel (.xlsx) file containing the data flow information.")

# File uploader widget
uploaded_file = st.sidebar.file_uploader("Choose an Excel file", type=["xlsx"])

# List of expected columns
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

# Function to process data
def process_data(file):
    try:
        # Read Excel file into DataFrame
        df = pd.read_excel(file)
        # Check if the expected columns exist in the file
        missing_cols = [col for col in expected_columns if col not in df.columns]
        if missing_cols:
            st.error(f"Missing expected columns: {', '.join(missing_cols)}")
            return None
        # Optionally, you could fill missing data or do further cleaning here
        df.fillna("N/A", inplace=True)
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

# Function to generate a data flow diagram using NetworkX
def generate_data_flow_diagram(df):
    G = nx.DiGraph()
    
    # For each row, create nodes and edges representing the data flow:
    # The typical flow will be: "Where data is sourced from" -> 
    # "Platform used to aggregate data" -> 
    # "Platform used to analyze data" -> 
    # "Platform used to publish curated data"
    #
    # We also annotate each node with compliance status if applicable.
    
    for idx, row in df.iterrows():
        source = row["Where data is sourced from"]
        agg = row["Platform used to aggregate data"]
        analysis = row["Platform used to analyze data"]
        publish = row["Platform used to publish curated data"]
        compliance = row["Compliance"]

        # Add nodes (if not already present)
        G.add_node(source)
        G.add_node(agg)
        G.add_node(analysis)
        G.add_node(publish)

        # Add edges for the data flow
        G.add_edge(source, agg)
        G.add_edge(agg, analysis)
        G.add_edge(analysis, publish)
        
        # Optionally, you can add compliance as an attribute on edges or nodes.
        # Here, we add compliance info as an edge attribute from analysis to publish.
        G[source][agg]['compliance'] = compliance
        G[agg][analysis]['compliance'] = compliance
        G[analysis][publish]['compliance'] = compliance

    # Drawing the network graph
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.5, seed=42)  # positions for all nodes

    # Draw nodes and edges
    nx.draw_networkx_nodes(G, pos, node_size=1500, node_color="lightblue")
    nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=20, edge_color="gray")
    nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
    
    # Create a legend for clarity
    plt.title("Data Flow Diagram")
    plt.axis("off")
    st.pyplot(plt.gcf())
    plt.clf()

# Function to generate an analysis summary
def generate_analysis_summary(df):
    st.subheader("Analysis Summary")
    st.write("Below is a summary of the key insights from the uploaded data:")

    # Display basic statistics for each key column
    for col in expected_columns:
        unique_values = df[col].unique()
        st.write(f"**{col}**: {len(unique_values)} unique value(s)")
    
    # Optionally, add more complex insights as needed
    st.write("This summary provides a quick overview of the diversity of values in each column.")

# Main application logic
if uploaded_file is not None:
    # Process the uploaded Excel file
    data = process_data(uploaded_file)
    
    if data is not None:
        # Show data preview: display the first few rows
        st.subheader("Data Preview")
        st.write(data.head())

        # Generate and display the data flow diagram
        st.subheader("Data Flow Diagram")
        generate_data_flow_diagram(data)

        # Display analysis summary
        generate_analysis_summary(data)
else:
    st.info("Please upload an Excel file to proceed.")
