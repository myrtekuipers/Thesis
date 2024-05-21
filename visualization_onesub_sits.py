import sqlite3
from sqlite3 import Error 
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

database = 'databases/hoesten.sqlite3'

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
    source_id, subjectTitle, subjectICPC = subject_info_task

    G.add_node(source_id, subjectTitle=subjectTitle, subjectICPC=subjectICPC)

    return source_id

def get_related_situations():
    cur.execute('''
        SELECT d.situationId, s.situationTitle, s.situationICPC
        FROM dblinks d
        JOIN situations s ON d.situationId = s.situationId

    ''')

        #     JOIN snomedlinks sl ON d.snomedlinkId = sl.linkid
        # WHERE sl.similarity = 1
    
    related_situation_data = cur.fetchall()

    return related_situation_data

def get_related_situations_freq(related_situation_data):
    cur.execute('''
        SELECT sl.snomedlinkId, GROUP_CONCAT(DISTINCT d.situationId) AS situation_ids
        FROM dblinks d
        JOIN snomedlinks sl ON d.snomedlinkId = sl.snomedlinkId
        GROUP BY sl.snomedlinkId
    ''')

    results = cur.fetchall()

    situation_occurrences = {}

    for row in results:
        value = row[1]
        if value is not None:
            situation_ids = value.split(',') 
            for situation_id1 in situation_ids:
                if situation_id1 in [str(row[0]) for row in related_situation_data]: 
                    if situation_id1 not in situation_occurrences:
                        situation_occurrences[situation_id1] = 1
                    else:
                        situation_occurrences[situation_id1] += 1

    return situation_occurrences

def add_related_situations_nodes_edges(related_situation_data, situation_occurrences, source_id):
    for related_situation_id, related_situationTitle, related_situationICPC in related_situation_data:
        G.add_node(related_situation_id, situationTitle=related_situationTitle, situationICPC=related_situationICPC)
        if str(related_situation_id) in situation_occurrences:
            occurrences = situation_occurrences.get(str(related_situation_id))
            G.add_edge(source_id, related_situation_id, weight = occurrences)


def add_related_subjects_nodes_edges(related_situation_data):
    for situation_id, _, _ in related_situation_data:
        cur.execute('''
            SELECT d.subjectId, sub.subjectTitle, sub.subjectICPC
            FROM dblinks d
            JOIN subjects sub ON d.subjectId = sub.subjectId
            JOIN situations s ON d.subjectId = s.subjectId
            WHERE s.situationId = ?
        ''', (situation_id,))
        related_subjects = cur.fetchall()

        for related_subject_id, related_subject_title, related_subject_icpc in related_subjects:
            G.add_node(related_subject_id, subjectTitle = related_subject_title, subjectICPC = related_subject_icpc)
            G.add_edge(situation_id, related_subject_id, weight = 1)

def add_node_labels():
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

    return node_labels

def add_node_colors(source_id):
    # color_mapping = {
    #     range(1, 30): 'blue',    # Symptomen en klachten
    #     range(30, 50): 'orange',    # Diagnostische/preventieve verrichtingen
    #     range(50, 60): 'green',  # Medicatie/therapeutische verrichtingen
    #     range(60, 62): 'black', # Uitslagen van onderzoek
    #     62: 'cyan',            # Administratieve verrichtingen
    #     range(63, 70): 'purple', # Verwijzingen/andere verrichtingen
    #     range(70, 100): 'red'   # Omschreven ziekten
    # }

    node_colors = []
    for node in G.nodes:
        if node == source_id:
            color = 'yellow'
        elif 'subjectICPC' in G.nodes[node]:
            color = 'red'
        elif 'situationICPC' in G.nodes[node]:
            color = 'orange'
        node_colors.append(color)
        # if colors:
        #     most_common_colors = Counter(colors).most_common() 
        #     most_common_color = most_common_colors[0] 
        #     if len(most_common_colors) > 1:
        #         node_colors.append('pink')  
        #     else:
        #         node_colors.append(most_common_color)  
        # else:
        #     node_colors.append('gray') 

    return node_colors

def add_legend():
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label='Symptomen en klachten', markerfacecolor='blue', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Diagnostische/preventieve verrichtingen', markerfacecolor='orange', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Medicatie/therapeutische verrichtingen', markerfacecolor='green', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Uitslagen van onderzoek', markerfacecolor='black', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Administratieve verrichtingen', markerfacecolor='cyan', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Verwijzingen/andere verrichtingen', markerfacecolor='purple', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Omschreven ziekten', markerfacecolor='red', markersize=10)]

    plt.legend(handles=legend_elements, loc='upper right')

def draw_graph(node_labels, node_colors):
    pos = nx.spring_layout(G)
    plt.axis('off')
    #add_legend()
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color='black')
    nx.draw(G, pos, with_labels=False, node_size=1000, edge_color='gray', node_color = node_colors, arrowsize=10)
    edge_labels = {(u, v): str(G.edges[u, v]['weight']) for u, v in G.edges() if G.edges[u, v]['weight'] != 1}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    plt.title('Subject Relationships')
    plt.show()
    plt.close()

def main():
    source_subject = "Hoesten"

    source_id = get_subject_info(source_subject)
    related_situation_data = get_related_situations()
    situation_occurrences = get_related_situations_freq(related_situation_data)
    add_related_situations_nodes_edges(related_situation_data, situation_occurrences, source_id)
    add_related_subjects_nodes_edges(related_situation_data)
    node_labels = add_node_labels()
    node_colors = add_node_colors(source_id)
    draw_graph(node_labels, node_colors)

if __name__ == '__main__':
    main()