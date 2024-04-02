import sqlite3
import networkx as nx
import matplotlib.pyplot as plt

# Connect to your SQLite database
conn = sqlite3.connect('data/test2.sqlite3')
cursor = conn.cursor()

# Fetch the subject ID corresponding to the given task ID
task_id = 452
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
subject_data = cursor.fetchone()  # Using fetchone since we're expecting one subject

# Extract subject information
subject_id, subjectTitle, subjectICPC = subject_data

# Create a directed graph
G = nx.DiGraph()

# Add the subject node
G.add_node(subject_id)
G.nodes[subject_id]['subjectTitle'] = subjectTitle
G.nodes[subject_id]['subjectICPC'] = subjectICPC

# Fetch and add related subject IDs
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
               SELECT s.situationId, s.situationTitle, s.situationICPC
               FROM situations s
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
               
related_situations = cursor.fetchall()

# Add edges to the graph connecting the subject nodes
for related_situation_id, related_situation_title, related_situation_icpc in related_situations:
    G.add_node(related_situation_id)
    G.nodes[related_situation_id]['subjectTitle'] = related_situation_title
    G.nodes[related_situation_id]['subjectICPC'] = related_situation_icpc
    G.add_edge(subject_id, related_situation_id)


#get the subject_id belong to the situation_id
cursor.execute('''
    SELECT sub.subjectId, sub.subjectTitle, sub.subjectICPC
    FROM subjects sub
    JOIN situations s ON sub.subjectId = s.subjectId
    WHERE s.situationId = ?
''', (related_situation_id,))

related_subjects = cursor.fetchall()

# Add edges to the graph connecting the subject nodes
for related_subject_id, related_subject_title, related_subject_icpc in related_subjects:
    G.add_node(related_subject_id)
    G.nodes[related_subject_id]['subjectTitle'] = related_subject_title
    G.nodes[related_subject_id]['subjectICPC'] = related_subject_icpc
    G.add_edge(related_situation_id, related_subject_id)

# Close the database connection
conn.close()

# Draw the graph
pos = nx.spring_layout(G)  # Define node positions
nx.draw(G, pos, with_labels=False)

node_labels = {}
for node in G.nodes:
    label = f"{node}\n"
    if 'subjectTitle' in G.nodes[node]:
        label += f"{G.nodes[node]['subjectTitle']}\n"
    if 'subjectICPC' in G.nodes[node]:
        label += f"ICPC: {G.nodes[node]['subjectICPC']}\n"
    if 'situationTitle' in G.nodes[node]:
        label += f"Situation Title: {G.nodes[node]['situationTitle']}\n"
    if 'situationICPC' in G.nodes[node]:
        label += f"Situation ICPC: {G.nodes[node]['situationICPC']}\n"

    node_labels[node] = label

nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color='black')
plt.show()
