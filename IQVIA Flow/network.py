import pandas as pd
import os
import networkx as nx
import matplotlib.pyplot as plt

# Path to the main directory containing subfolders
main_folder_path = (
    "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/RAW"
)

# Load the source mapping Excel file (update the file path accordingly)
source_mapping_file = "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/Source Master Mapping/Source_master.xlsx"

# Load the Excel file into a DataFrame
source_mapping_df = pd.read_excel(source_mapping_file)

# Create a directed graph
G = nx.DiGraph()

# Dictionary to map Source Name to Source ID, Source Type, and File Type
source_mapping = {
    row["Source Name"]: {
        "Source ID": row["Source Id"],
        "Source Type": row["Source Type"],
        "File Type": row["File Type"],
    }
    for _, row in source_mapping_df.iterrows()
}

# Function to get source information (ID, Type, and File Type) from the mapping
def get_source_info(source_name):
    normalized_source_name = source_name.strip()
    print(f"Normalized Source Name: {normalized_source_name}")
    return source_mapping.get(normalized_source_name, None)

# Dictionary to track column names and their sources for comparison
column_sources = {}

# Walk through the subfolders and files in the main folder
for subdir, dirs, files in os.walk(main_folder_path):
    if subdir == main_folder_path:
        continue

    source_name = os.path.basename(subdir).strip()
    print(f"Extracted Source Name: {source_name}")

    source_info = get_source_info(source_name)
    if source_info is None:
        print(f"Warning: Source Name '{source_name}' not found in the mapping. Skipping.")
        continue

    source_id = source_info["Source ID"]
    source_type = source_info["Source Type"]
    file_type = source_info["File Type"]

    # Add source node to graph
    G.add_node(source_name, node_type='source', source_id=source_id, 
               source_type=source_type, file_type=file_type)

    file_id_counter = 1
    for file_name in files:
        print(f"Processing file: {file_name}")

        if not (file_name.endswith(".csv") or file_name.endswith(".xlsx")):
            continue

        file_path = os.path.join(subdir, file_name)
        file_name_without_extension = os.path.splitext(file_name)[0]

        file_id = file_id_counter
        file_id_counter += 1

        # Add file node and edge from source to file
        G.add_node(file_name_without_extension, node_type='file', file_id=file_id)
        G.add_edge(source_name, file_name_without_extension)

        if file_name.endswith(".csv"):
            df = pd.read_csv(file_path, nrows=100)
        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(file_path, nrows=100)

        for index, column in enumerate(df.columns, 1):
            if column not in column_sources:
                column_sources[column] = []
                # Add column node
                G.add_node(column, node_type='column')
            
            # Add edge from file to column
            G.add_edge(file_name_without_extension, column)
            
            column_sources[column].append({
                "source": source_name,
                "file_name": file_name_without_extension,
                "file_id": file_id,
                "column_sequence": index,
            })

# Draw the network
plt.figure(figsize=(15, 10))
pos = nx.spring_layout(G)

# Draw nodes with different colors based on type
source_nodes = [n for n,d in G.nodes(data=True) if d.get('node_type')=='source']
file_nodes = [n for n,d in G.nodes(data=True) if d.get('node_type')=='file']
column_nodes = [n for n,d in G.nodes(data=True) if d.get('node_type')=='column']

nx.draw_networkx_nodes(G, pos, nodelist=source_nodes, node_color='lightblue', node_size=2000)
nx.draw_networkx_nodes(G, pos, nodelist=file_nodes, node_color='lightgreen', node_size=1500)
nx.draw_networkx_nodes(G, pos, nodelist=column_nodes, node_color='pink', node_size=1000)

# Draw edges and labels
nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True)
nx.draw_networkx_labels(G, pos)

plt.title("Data Source Network")
plt.axis('off')
plt.show()
