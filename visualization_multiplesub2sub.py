import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import csv

conn = sqlite3.connect('data/acne.sqlite3')
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

    G.add_node(subject_id, subjectTitle=subjectTitle, subjectICPC=subjectICPC)

    source_nodes.append(subject_id)

    # cursor.execute('''
    #     SELECT sl.snomedlinkId, GROUP_CONCAT(DISTINCT s.subjectId) AS subject_ids
    #     FROM dblinks d
    #     JOIN situations s ON d.situationId = s.situationId
    #     JOIN snomedlinks sl ON d.snomedlinkId = sl.snomedlinkId
    #     JOIN termcandidates tc ON sl.termId = tc.termId
    #     WHERE tc.taskId = ?
    #     GROUP BY sl.snomedlinkId
    # ''', (task_id,))
    
    cursor.execute('''
    SELECT sl.snomedlinkId, GROUP_CONCAT(DISTINCT d.subjectId) AS subject_ids
    FROM dblinks d
    JOIN snomedlinks sl ON d.snomedlinkId = sl.snomedlinkId
    JOIN termcandidates tc ON sl.termId = tc.termId
    WHERE tc.taskId = ?
    GROUP BY sl.snomedlinkId
    ''', (task_id,))

    results = cursor.fetchall()


    subject_occurrences = {}

    for row in results:
        subject_ids = row[1].split(',') 
        
        for subject_id1 in subject_ids:
            if subject_id1 not in subject_occurrences:
                subject_occurrences[subject_id1] = 1
            else:
                subject_occurrences[subject_id1] += 1

    #
    
    # cursor.execute('''
    #     SELECT s.subjectId, sub.subjectTitle, sub.subjectICPC
    #     FROM situations s
    #     JOIN subjects sub ON s.subjectId = sub.subjectId
    #     WHERE s.situationId IN (
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
    # ''', (task_id,))

    cursor.execute('''
    SELECT s.subjectId, sub.subjectTitle, sub.subjectICPC
    FROM dblinks d
    JOIN subjects sub ON d.subjectId = sub.subjectId
    JOIN situations s ON d.situationId = s.situationId
    JOIN snomedlinks sl ON d.snomedlinkId = sl.snomedlinkId
    JOIN termcandidates tc ON sl.termId = tc.termId
    WHERE tc.taskId = ?
    ''', (task_id,))

    related_subject_data = cursor.fetchall()

    for related_subject_id, related_subjectTitle, related_subjectICPC in related_subject_data:
        if subject_id != related_subject_id:  
            G.add_node(related_subject_id, subjectTitle=related_subjectTitle, subjectICPC=related_subjectICPC)
            if str(related_subject_id) in subject_occurrences:
                occurrences = subject_occurrences.get(str(related_subject_id))
                G.add_edge(subject_id, related_subject_id, weight=occurrences)

conn.close()

pos = nx.spring_layout(G)

node_labels = {}
for node in G.nodes:
    label = f"{node}\n"
    if 'subjectTitle' in G.nodes[node]:
        label += f"{G.nodes[node]['subjectTitle']}\n"
    if 'subjectICPC' in G.nodes[node]:
        label += f"ICPC: {G.nodes[node]['subjectICPC']}\n"
    node_labels[node] = label

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
        icpc_values = G.nodes[node]['subjectICPC'].replace(" ", "").split(",") 
        colors = [] 
        for icpc_value in icpc_values:
            if icpc_value == '': 
                continue
            for key, value in color_mapping.items():
                if isinstance(key, range):
                    if int(icpc_value[1:3]) in key:
                        colors.append(value)
    if colors:
        most_common_colors = Counter(colors).most_common() 
        most_common_color, count = most_common_colors[0] 
        if len(most_common_colors) > 1:
            node_colors.append('pink')  
        else:
            node_colors.append(most_common_color)  
    else:
        node_colors.append('gray') 


#add a legend with symptomen en klachten, diagnostische/preventieve verrichtingen, medicatie/therapeutische verrichtingen, uitslagen van onderzoek, administratieve verrichtingen, verwijzingen/andere verrichtingen, omschreven ziekten
#plt.figure(figsize=(10, 10))
plt.axis('off')

legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label='Symptomen en klachten', markerfacecolor='blue', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Diagnostische/preventieve verrichtingen', markerfacecolor='orange', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Medicatie/therapeutische verrichtingen', markerfacecolor='green', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Uitslagen van onderzoek', markerfacecolor='black', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Administratieve verrichtingen', markerfacecolor='cyan', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Verwijzingen/andere verrichtingen', markerfacecolor='purple', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Omschreven ziekten', markerfacecolor='red', markersize=10)]

plt.legend(handles=legend_elements, loc='upper right')




nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color='black')


nx.draw(G, pos, with_labels=False, node_size=1000, node_color=node_colors, edge_color='gray', arrowsize=10)

edge_labels = {(u, v): str(G.edges[u, v]['weight']) for u, v in G.edges() if G.edges[u, v]['weight'] != 1}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

plt.title('Subject Relationships')
plt.show()
