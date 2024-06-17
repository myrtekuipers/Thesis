import sqlite3
from sqlite3 import Error 
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import re
import numpy as np
import my_networkx as my_nx
from pyvis.network import Network

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

    subject_id = str(subject_id)

    if not G.has_node(subject_id):
        G.add_node(subject_id, subjectTitle=subjectTitle, subjectICPC=subjectICPC)

    return subject_id, subjectTitle

def get_info_related_subjects(source_id, source_title, links_list, links):
    subject_pattern = rf"Subject: {source_id} {re.escape(source_title)} \((.*?)\)"

    subject_line = re.search(subject_pattern, links)

    if not subject_line:
        return None, []
    
    start_pos = subject_line.end()
    
    end_pos = links.find('\nSubject:', start_pos)
    if end_pos == -1:
        end_pos = len(links)
    
    related_content = links[start_pos:end_pos].strip()

    pattern = re.compile(r"(\d+) (.+?) \(([^()]+)\) \((\d+)\)")
    related_subjects = re.findall(pattern, related_content)

    for id, title, icpc, occurrences in related_subjects:
        if not G.has_node(id):
            G.add_node(id, subjectTitle=title, subjectICPC=icpc)
            
        links_list.append((source_id, id))
        G.add_edge(source_id, id, weight=int(occurrences))
    
    return links_list

def add_node_labels():
    node_labels = {}
    for node in G.nodes:
        label = f"$\\bf{{{node}}}$\n"
        if 'subjectTitle' in G.nodes[node]:
            title = G.nodes[node]['subjectTitle']
            label += f"$\\bf{{{title}}}$\n".replace(" ", "\\ ")
        if 'subjectICPC' in G.nodes[node]:
            label += f"{G.nodes[node]['subjectICPC']}\n"
        node_labels[node] = label

    return node_labels

def add_node_colors(source_ids):
    color_mapping = {
        range(1, 30): 'cyan',    # Symptomen en klachten
        # range(30, 50): 'orange',    # Diagnostische/preventieve verrichtingen
        # range(50, 60): 'green',  # Medicatie/therapeutische verrichtingen
        # range(60, 62): 'black', # Uitslagen van onderzoek
        # 62: 'cyan',            # Administratieve verrichtingen
        # range(63, 70): 'purple', # Verwijzingen/andere verrichtingen
        range(70, 100): 'orange'   # Omschreven ziekten
    }

    node_colors_dict = {}
    for node in G.nodes:
        colors = []
        if node in source_ids:
            colors.append('yellow')
        else:
            icpc_values = G.nodes[node]['subjectICPC'].replace(" ", "").split(",")
            for icpc_value in icpc_values:
                if icpc_value == '':
                    continue
                for key, value in color_mapping.items():
                    if isinstance(key, range):
                        if int(icpc_value[1:3]) in key:
                            colors.append(value)
                    elif icpc_value == key:  # Assuming key could also be a specific value
                        colors.append(value)
                        
        if colors:
            most_common_colors = Counter(colors).most_common()
            most_common_color, _ = most_common_colors[0]
            if len(most_common_colors) > 1:
                node_colors_dict[node] = 'pink'
            else:
                node_colors_dict[node] = most_common_color
        else:
            node_colors_dict[node] = 'gray'

    return node_colors_dict

def add_legend():
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label='Symptomen and complaints', markerfacecolor='cyan', markersize=10),
                    #  plt.Line2D([0], [0], marker='o', color='w', label='Diagnostische/preventieve verrichtingen', markerfacecolor='orange', markersize=10),
                    #  plt.Line2D([0], [0], marker='o', color='w', label='Medicatie/therapeutische verrichtingen', markerfacecolor='green', markersize=10),
                    #  plt.Line2D([0], [0], marker='o', color='w', label='Uitslagen van onderzoek', markerfacecolor='black', markersize=10),
                    #  plt.Line2D([0], [0], marker='o', color='w', label='Administratieve verrichtingen', markerfacecolor='cyan', markersize=10),
                    #  plt.Line2D([0], [0], marker='o', color='w', label='Verwijzingen/andere verrichtingen', markerfacecolor='purple', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Predefined diseases', markerfacecolor='orange', markersize=10),
                     plt.Line2D([0], [0], marker='o', color='w', label='Combination of both categories', markerfacecolor='pink', markersize=10)]

    plt.legend(handles=legend_elements, loc='lower left')

def change_edge_width(edges):
    edge_width = {edge: G.edges[edge]['weight'] for edge in edges}
    return edge_width

def draw_source_edges(G, pos, source_ids, curved_edges):
    for i in range(len(source_ids)):
        for j in range(len(source_ids)):
            if i != j:
                if G.has_edge(source_ids[i], source_ids[j]) and G.has_edge(source_ids[j], source_ids[i]):
                    edge = (source_ids[i], source_ids[j])
                    width = G.edges[edge]['weight']
                    arc_rad = 0.1
                    nx.draw_networkx_edges(G, pos, edgelist=[edge], width=width, edge_color='green', alpha = 0.4, connectionstyle=f'arc3, rad = {arc_rad}')
                    curved_edge_labels = {edge: G.edges[edge]['weight'] for edge in curved_edges if G.edges[edge]['weight'] != 1}
                    my_nx.my_draw_networkx_edge_labels(G, pos, edge_labels=curved_edge_labels,rotate=False,rad = arc_rad, font_size = 7)
                elif G.has_edge(source_ids[i], source_ids[j]):
                    edge = (source_ids[i], source_ids[j])
                    width = G.edges[edge]['weight']
                    nx.draw_networkx_edges(G, pos, edgelist=[edge], width=width, edge_color='green', alpha=0.4)
                elif G.has_edge(source_ids[j], source_ids[i]):
                    edge = (source_ids[j], source_ids[i])
                    width = G.edges[edge]['weight']
                    nx.draw_networkx_edges(G, pos, edgelist=[edge], width=width, edge_color='green', alpha=0.4)


def draw_edges(pos, source_ids, node_colors_dict):
    curved_edges = [edge for edge in G.edges() if reversed(edge) in G.edges()]
    straight_edges = list(set(G.edges()) - set(curved_edges))

    edge_width_straight = change_edge_width(straight_edges)
    
    nx.draw_networkx_edges(G, pos, edgelist=edge_width_straight.keys(), width=list(edge_width_straight.values()), edge_color='purple', alpha = 0.4)
    
    straight_edge_labels = {edge: G.edges[edge]['weight'] for edge in straight_edges if G.edges[edge]['weight'] != 1}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=straight_edge_labels, rotate=False, font_size=7)

    draw_source_edges(G, pos, source_ids, curved_edges)

def draw_nodes(pos, node_labels, node_colors_dict):
    node_colors = [node_colors_dict[node] for node in G.nodes()]

    nx.draw_networkx_nodes(G,
                           pos,
                           node_color=node_colors,
                           node_size=500,
                           alpha=0.8)
    
    nx.draw_networkx_labels(G, 
                            pos, 
                            labels=node_labels, 
                            font_size=7, 
                            font_color='black')

def improve_layout(pos, node_colors_dict):
    unique_colors = set(node_colors_dict.values())
    angs = np.linspace(0, 2*np.pi, 1+len(unique_colors))
    rad = 3.0
    
    repos = []
    color_to_posx = {}
    for i, color in enumerate(unique_colors):
        if i > 0:
            offset_x = rad * np.cos(angs[i])
            offset_y = rad * np.sin(angs[i])
            repos.append(np.array([offset_x, offset_y]))
        color_to_posx[color] = i

    for node, color in node_colors_dict.items():
        posx = color_to_posx[color]
        if posx > 0:
            pos[node] += repos[posx - 1]

def draw_graph(source_ids, node_labels, node_colors_dict, links_file_name):

    pos = nx.circular_layout(G)
    plt.axis('off')

    improve_layout(pos, node_colors_dict)

    draw_nodes(pos, node_labels, node_colors_dict)
    
    draw_edges(pos, source_ids, node_colors_dict)

    #plt.title(f'Subject Relationships using {links_file_name}')
    add_legend()
    plt.show()
    plt.close()

    return G

def main():
    source_subjects = ["Hoesten", "Keelpijn"]

    links_file_name = 'filter1_a'

    with open(f'links/{links_file_name}.txt', 'r') as file:
        links = file.read()

    source_ids = []
    links_list = []
    for source_subject in source_subjects:
        source_id, source_title = get_subject_info(source_subject)
        source_ids.append(source_id)
        links_list = get_info_related_subjects(source_id, source_title, links_list, links)

    node_labels = add_node_labels()
    node_colors = add_node_colors(source_ids) 
    draw_graph(source_ids, node_labels, node_colors, links_file_name)

if __name__ == '__main__':
    main()