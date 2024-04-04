import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import csv

conn = sqlite3.connect('data/test.sqlite3')
cursor = conn.cursor()

G = nx.DiGraph()

cursor.execute('''
    SELECT DISTINCT taskId
    FROM termcandidates
''')
task_ids = cursor.fetchall()
source_nodes = []
for task_id in task_ids:
    
    task_id = task_id[0]

    cursor.execute('''
        SELECT sub.subjectId, sub.subjectTitle, sub.subjectICPC
        FROM subjects sub
        JOIN situations s ON sub.subjectId = s.subjectId
        WHERE s.situationId = (
            SELECT situationId
            FROM tasks
            WHERE taskId = ?
        )
    ''', (task_id,))
    subject_info_task = cursor.fetchone()  # only one subject id corresponding to that task id

    subject_id, subjectTitle, subjectICPC = subject_info_task

    # Add subject as a node to the graph
    G.add_node(subject_id, subjectTitle=subjectTitle, subjectICPC=subjectICPC)

    #add the subject node corresponding to the task id as source node
    source_nodes.append(subject_id)

    # cursor.execute('''
    # SELECT s.subjectId, COUNT(*) AS occurrences
    #     FROM dblinks d
    #     JOIN situations s ON d.situationId = s.situationId
    #     WHERE d.situationId IN (
    #         SELECT d.situationId
    #         FROM dblinks d
    #         WHERE d.snomedlinkId IN (
    #             SELECT sl.snomedlinkId
    #             FROM snomedlinks sl
    #             WHERE sl.termId IN (
    #                 SELECT tc.termId
    #                 FROM termcandidates tc
    #                 WHERE tc.taskId = ?
    #             )
    #         )
    #     )
    #     GROUP BY s.subjectId

    # ''', (task_id,))

    cursor.execute('''
    SELECT d.icpc, COUNT(DISTINCT sl.snomedlinkId) AS occurrences
    FROM dblinks d
    JOIN snomedlinks sl ON d.snomedlinkId = sl.snomedlinkId
    JOIN termcandidates tc ON sl.termId = tc.termId
    WHERE tc.taskId = ?
    GROUP BY d.icpc
''', (task_id,))

    
    # Fetch the results
    results = cursor.fetchall()

    #delete the source node subject id from the results
    #results = [result for result in results if result[0] != subject_id]

    print(results)

    # # Write results to CSV file
    # with open('data/testing.csv', 'w', newline='') as csvfile:
    #     csv_writer = csv.writer(csvfile)
    #     csv_writer.writerow(['subject_id', 'occurrences'])  # Write header
    #     csv_writer.writerows(results)  # Write rows

    # print("Results saved to", 'data/testing.csv')

    
    # Get related subjects
    cursor.execute('''
        SELECT s.subjectId, sub.subjectTitle, sub.subjectICPC
        FROM situations s
        JOIN subjects sub ON s.subjectId = sub.subjectId
        WHERE s.situationId IN (
            SELECT d.situationId
            FROM dblinks d
            WHERE d.snomedlinkId IN (
                SELECT sl.snomedlinkId
                FROM snomedlinks sl
                WHERE sl.termId IN (
                    SELECT tc.termId
                    FROM termcandidates tc
                    WHERE tc.taskId = ?
                )
            )
        )
    ''', (task_id,))

    related_subject_data = cursor.fetchall()

    # Add related subjects as nodes and edges to the graph
    # for related_subject_id, related_subjectTitle, related_subjectICPC in related_subject_data:
    #     G.add_node(related_subject_id, subjectTitle=related_subjectTitle, subjectICPC=related_subjectICPC)
    #     G.add_edge(subject_id, related_subject_id)
    for related_subject_id, related_subjectTitle, related_subjectICPC in related_subject_data:
        G.add_node(related_subject_id, subjectTitle=related_subjectTitle, subjectICPC=related_subjectICPC)
        weight = None
        for result in results:
            if result[0] == related_subject_id:
                weight = result[1]
                break
        G.add_edge(subject_id, related_subject_id, weight=weight)  # Add edge with weight

        

        
conn.close()

# Draw the graph with Kamada-Kawai layout for better clustering
pos = nx.kamada_kawai_layout(G)

# Add node labels
node_labels = {node: f"{G.nodes[node]['subjectTitle']}\nICPC: {G.nodes[node]['subjectICPC']}" for node in G.nodes}

color_mapping = {
        range(1, 30): 'blue',    # Symptomen en klachten
        range(30, 50): 'orange',    # Diagnostische/preventieve verrichtingen
        range(50, 60): 'green',  # Medicatie/therapeutische verrichtingen
        range(60, 62): 'black', # Uitslagen van onderzoek
        62: 'cyan',            # Administratieve verrichtingen
        range(63, 70): 'purple', # Verwijzingen/andere verrichtingen
        range(70, 100): 'red'   # Omschreven ziekten
    }

node_colors = []
for node in G.nodes:
    colors = []
    if node in source_nodes:
        colors.append('yellow')
    elif 'subjectICPC' in G.nodes[node]:
        icpc_values = G.nodes[node]['subjectICPC'].replace(" ", "").split(",")  # split ICPC codes if there are multiple and delete the spaces for workability
        colors = []  # use a list to store all colors for multiple ICPC codes
        for icpc_value in icpc_values:
            if icpc_value == '': #if there is no ICPC code assigned, continue
                continue
            for key, value in color_mapping.items():
                if isinstance(key, range):
                    if int(icpc_value[1:3]) in key:
                        colors.append(value)
        # if there are multiple colors (multiple ICPC codes), determine the most common color for the node
    if colors:
        most_common_colors = Counter(colors).most_common()  # Get all most common colors
        most_common_color, count = most_common_colors[0]  # Get the first most common color
        if len(most_common_colors) > 1:  # Check if there's a tie in colors
            node_colors.append('pink')  # Make the node pink if there's a tie
        else:
            node_colors.append(most_common_color)  # Use the most common color otherwise
    else:
        node_colors.append('gray')  # Default color if no ICPC value is available

# Add edge labels
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color='black')

# # Draw nodes and edges
# nx.draw(G, pos, with_labels=False, node_size=1000, node_color=node_colors, edge_color='gray', arrowsize=10)

# plt.title('Subject Relationships')
# plt.show()

# Draw node labels
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color='black')

# Draw nodes and edges
nx.draw(G, pos, with_labels=False, node_size=1000, node_color=node_colors, edge_color='gray', arrowsize=10)

# Add edge labels
edge_labels = {(u, v): str(G.edges[u, v]['weight']) for u, v in G.edges()}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

plt.title('Subject Relationships')
plt.show()
