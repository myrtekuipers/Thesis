import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

conn = sqlite3.connect('data/test2.sqlite3')
cursor = conn.cursor()

# get the subject info corresponding to the given task ID
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
subject_info_task = cursor.fetchone() #only one subject id corresponding to that task id

subject_id, subjectTitle, subjectICPC = subject_info_task

G = nx.DiGraph()

#add the subject node corresponding to the task id as source node
G.add_node(subject_id)
G.nodes[subject_id]['subjectTitle'] = subjectTitle
G.nodes[subject_id]['subjectICPC'] = subjectICPC

#get the subject ids corresponding to the situation ids in dblinks, in order to get the related subjects
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

for related_subject_id, related_subjectTitle, related_subjectICPC in related_subject_data:
    G.add_node(related_subject_id)
    G.nodes[related_subject_id]['subjectTitle'] = related_subjectTitle
    G.nodes[related_subject_id]['subjectICPC'] = related_subjectICPC
    G.add_edge(subject_id, related_subject_id)

# #draw the graph
pos = nx.spring_layout(G)  

# #add the title and icpc for every node
node_labels = {}
for node in G.nodes:
    label = f"{node}\n"
    if 'subjectTitle' in G.nodes[node]:
        label += f"{G.nodes[node]['subjectTitle']}\n"
    if 'subjectICPC' in G.nodes[node]:
        label += f"ICPC: {G.nodes[node]['subjectICPC']}\n"
    node_labels[node] = label

# Define color mapping based on ICPC codes
color_mapping = {
    range(1, 30): 'blue',    # Symptomen en klachten
    range(30, 50): 'red',    # Diagnostische/preventieve verrichtingen
    range(50, 60): 'green',  # Medicatie/therapeutische verrichtingen
    range(60, 62): 'yellow', # Uitslagen van onderzoek
    62: 'orange',            # Administratieve verrichtingen
    range(63, 70): 'purple', # Verwijzingen/andere verrichtingen
    range(70, 100): 'cyan'   # Omschreven ziekten
}

# Assign colors to nodes based on their ICPC values
node_colors = []
for node in G.nodes:
    if 'subjectICPC' in G.nodes[node]:
        icpc_values = G.nodes[node]['subjectICPC'].replace(" ", "").split(",")  # Split ICPC codes if there are multiple
        colors = []  # Use a list to store all colors for multiple ICPC codes
        for icpc_value in icpc_values:
            if icpc_value == '':
                continue
            for key, value in color_mapping.items():
                if isinstance(key, range):
                    if int(icpc_value[1:3]) in key:
                        colors.append(value)
                else:
                    if int(icpc_value[1:3]) == key:
                        colors.append(value)
        # Determine the most common color for the node
        if colors:
            most_common_colors = Counter(colors).most_common()  # Get all most common colors
            most_common_color, count = most_common_colors[0]  # Get the first most common color
            if len(most_common_colors) > 1:  # Check if there's a tie in colors
                node_colors.append('pink')  # Make the node pink if there's a tie
            else:
                node_colors.append(most_common_color)  # Use the most common color otherwise
        else:
            node_colors.append('gray')  # Default color if no ICPC value is available
    else:
        node_colors.append('gray')  # Default color if ICPC value is not available

# Draw the graph with node colors
nx.draw(G, pos, with_labels=False, node_color=node_colors)

# Add labels to the graph
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color='black')

# Show the graph
plt.show()