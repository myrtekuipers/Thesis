import sqlite3
from sqlite3 import Error 
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

database = 'databases/combined.sqlite3'

try: 
    conn = sqlite3.connect(database)
except Error as e:
    print(e)

cur = conn.cursor()

G = nx.DiGraph()

def get_subject_info(source_subject):
    cur.execute('''
        SELECT subjectId, subjectTitle, subjectICPC
        FROM subjects 
        WHERE subjectTitle = ?
    ''', (source_subject,))

    subject_info_task = cur.fetchone()  
    subject_id, subjectTitle, subjectICPC = subject_info_task

    G.add_node(subject_id, subjectTitle=subjectTitle, subjectICPC=subjectICPC)

    return subject_id

def get_task_ids(source_id):
    cur.execute('''
        SELECT t.taskId
        FROM tasks t
        JOIN situations s ON t.situationId = s.situationId
        JOIN subjects sub ON s.subjectId = sub.subjectId 
        WHERE sub.subjectId = ?
    ''', (source_id,))

    task_ids = cur.fetchall()

    get_related_subjects_freq(task_ids, source_id)

def get_related_subjects_freq(task_ids, source_id):
    subject_occurrences = []

    for task_id in task_ids:
        task_id = task_id[0]

        cur.execute('''
        SELECT d.subjectId, s.subjectTitle, s.subjectICPC,
        COUNT(DISTINCT sl.snomedlinkId) AS occurrences
        FROM dblinks d
        JOIN subjects s ON d.subjectId = s.subjectId
        JOIN snomedlinks sl ON d.snomedlinkId = sl.snomedlinkId
        JOIN termcandidates tc ON sl.termId = tc.termId
        WHERE tc.taskId = ?
        GROUP BY d.subjectId;   
        ''' , (task_id,))

        results = cur.fetchall()

        if source_id in [row[0] for row in results]:
            results = [row for row in results if row[0] != source_id]

        subject_occurrences.extend(results)

        aggregated_data = {}

        for subject_id, title, icpc, frequency in subject_occurrences:
            if subject_id in aggregated_data:
                aggregated_data[subject_id]['frequency'] += frequency
            else:
                aggregated_data[subject_id] = {'title': title, 'icpc': icpc, 'frequency': frequency}

        aggregated_list = [(subject_id, data['title'], data['icpc'], data['frequency']) for subject_id, data in aggregated_data.items()]

    add_related_nodes_edges(aggregated_list, source_id)

def add_related_nodes_edges(subject_occurrences, source_id):
    for related_subject_id, related_subjectTitle, related_subjectICPC, occurrences in subject_occurrences:
            G.add_node(related_subject_id, subjectTitle=related_subjectTitle, subjectICPC=related_subjectICPC)
            G.add_edge(source_id, related_subject_id, weight=occurrences)

def add_node_labels():
    node_labels = {}
    for node in G.nodes:
        label = f"{node}\n"
        if 'subjectTitle' in G.nodes[node]:
            label += f"{G.nodes[node]['subjectTitle']}\n"
        if 'subjectICPC' in G.nodes[node]:
            label += f"ICPC: {G.nodes[node]['subjectICPC']}\n"
        node_labels[node] = label

    return node_labels

def add_node_colors(source_ids):
    color_mapping = {
        range(1, 30): 'blue',    # Symptomen en klachten
        # range(30, 50): 'orange',    # Diagnostische/preventieve verrichtingen
        # range(50, 60): 'green',  # Medicatie/therapeutische verrichtingen
        # range(60, 62): 'black', # Uitslagen van onderzoek
        # 62: 'cyan',            # Administratieve verrichtingen
        # range(63, 70): 'purple', # Verwijzingen/andere verrichtingen
        range(70, 100): 'red'   # Omschreven ziekten
    }

    node_colors = []
    for node in G.nodes:
        colors = []
        if node in source_ids:
            colors.append('yellow')
        else:
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
            most_common_color,_ = most_common_colors[0] 
            if len(most_common_colors) > 1:
                node_colors.append('pink')  
            else:
                node_colors.append(most_common_color)  
        else:
            node_colors.append('gray') 

    return node_colors

def add_legend():
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label='Symptomen en klachten', markerfacecolor='blue', markersize=10),
                    #  plt.Line2D([0], [0], marker='o', color='w', label='Diagnostische/preventieve verrichtingen', markerfacecolor='orange', markersize=10),
                    #  plt.Line2D([0], [0], marker='o', color='w', label='Medicatie/therapeutische verrichtingen', markerfacecolor='green', markersize=10),
                    #  plt.Line2D([0], [0], marker='o', color='w', label='Uitslagen van onderzoek', markerfacecolor='black', markersize=10),
                    #  plt.Line2D([0], [0], marker='o', color='w', label='Administratieve verrichtingen', markerfacecolor='cyan', markersize=10),
                    #  plt.Line2D([0], [0], marker='o', color='w', label='Verwijzingen/andere verrichtingen', markerfacecolor='purple', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Omschreven ziekten', markerfacecolor='red', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Combinatie van beiden', markerfacecolor='pink', markersize=10)]

    plt.legend(handles=legend_elements, loc='upper right')


def draw_graph(node_labels, node_colors):
    pos = nx.fruchterman_reingold_layout(G)
    plt.axis('off')
    add_legend()
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color='black')
    nx.draw(G, pos, with_labels=False, node_size=1000, node_color = node_colors, edge_color='gray', arrowsize=10)
    edge_labels = {(u, v): str(G.edges[u, v]['weight']) for u, v in G.edges() if G.edges[u, v]['weight'] != 1}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    plt.title('Subject Relationships')
    plt.show()
    plt.close()

def main():
    source_subjects = ["Diabetes type 2"]

    source_ids = []
    for source_subject in source_subjects:
        source_id = get_subject_info(source_subject)
        source_ids.append(source_id)
        get_task_ids(source_id)

    node_labels = add_node_labels()
    node_colors = add_node_colors(source_ids)  
    draw_graph(node_labels, node_colors)

if __name__ == '__main__':
    main()