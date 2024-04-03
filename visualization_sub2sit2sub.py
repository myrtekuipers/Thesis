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

#get the situation ids from dblinks, in order to get the related situations
cursor.execute('''
    SELECT d.situationId, s.situationTitle, s.situationICPC
    FROM dblinks d
    JOIN situations s ON d.situationId = s.situationId
    JOIN snomedlinks sl ON d.snomedlinkId = sl.snomedlinkId
    JOIN termcandidates tc ON sl.termId = tc.termId
    WHERE tc.taskId = ?
''', (task_id,))
related_situation_data = cursor.fetchall()  

#add the situation nodes corresponding to the related situations from dblinks
for situation_id, situationTitle, situationICPC in related_situation_data:
    G.add_node(situation_id)
    G.nodes[situation_id]['situationTitle'] = situationTitle
    G.nodes[situation_id]['situationICPC'] = situationICPC
    G.add_edge(task_id, situation_id)

# get the subject ids corresponding to the related_situation ids
for situation_id, _, _ in related_situation_data:
    cursor.execute('''
        SELECT s.subjectId, sub.subjectTitle, sub.subjectICPC
        FROM situations s
        JOIN subjects sub ON s.subjectId = sub.subjectId
        WHERE s.situationId = ?
    ''', (situation_id,))
    related_subjects = cursor.fetchall()
    
    #for every situation_id, add the corresponding subject id as a node
    for related_subject_id, related_subject_title, related_subject_icpc in related_subjects:
        G.add_node(related_subject_id)
        G.nodes[related_subject_id]['subjectTitle'] = related_subject_title
        G.nodes[related_subject_id]['subjectICPC'] = related_subject_icpc
        G.add_edge(situation_id, related_subject_id)  

conn.close()

# draw the graph
pos = nx.spring_layout(G)  

# add the title and icpc for every node
node_labels = {}
for node in G.nodes:
    label = f"{node}\n"
    if 'subjectTitle' in G.nodes[node]:
        label += f"{G.nodes[node]['subjectTitle']}\n"
    if 'subjectICPC' in G.nodes[node]:
        label += f"ICPC: {G.nodes[node]['subjectICPC']}\n"
    if 'situationTitle' in G.nodes[node]:
        label += f"Situation: {G.nodes[node]['situationTitle']}\n"
    if 'situationICPC' in G.nodes[node]:
        label += f"Situation ICPC: {G.nodes[node]['situationICPC']}\n"
    node_labels[node] = label

# define color mapping based on ICPC codes
color_mapping = {
    range(1, 30): 'blue',    # Symptomen en klachten
    range(30, 50): 'orange',    # Diagnostische/preventieve verrichtingen
    range(50, 60): 'green',  # Medicatie/therapeutische verrichtingen
    range(60, 62): 'yellow', # Uitslagen van onderzoek
    62: 'cyan',            # Administratieve verrichtingen
    range(63, 70): 'purple', # Verwijzingen/andere verrichtingen
    range(70, 100): 'red'   # Omschreven ziekten
}

# assign colors to nodes based on their ICPC values
node_colors = []
for node in G.nodes:
    colors = []  
    if 'subjectICPC' in G.nodes[node]:
        icpc_values = G.nodes[node]['subjectICPC'].replace(" ", "").split(",")   # split ICPC codes if there are multiple and delete the spaces for workability
        for icpc_value in icpc_values:
            if icpc_value == '': #if there is no ICPC code assigned, continue
                continue
            for key, value in color_mapping.items():
                if isinstance(key, range):
                    if int(icpc_value[1:3]) in key:
                        colors.append(value)

    if 'situationICPC' in G.nodes[node]:
        icpc_values = G.nodes[node]['situationICPC'].replace(" ", "").split(",")  
        for icpc_value in icpc_values:
            if icpc_value == '':
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

nx.draw(G, pos, with_labels=False, node_color=node_colors)

# add labels to the graph
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color='black')

# Show the graph
plt.show()
