import re
import sys
import nltk
import networkx as nx
from operator import itemgetter

def write_list_to_file(filename, list_to_write):
    """
    Saves list contents to a file
    """
    inFile=open(filename,'w')
    string_list=[]
    for i in range(0,len(list_to_write)):
        string_list.append(str(list_to_write[i])) 
    inFile.write('\n'.join(string_list))
    inFile.close()

def load_file_as_list(filename_to_load):
    """
    returns file contents as a list where each line is an element of the list
    """
    inFile = open(filename_to_load)
    lines = inFile.readlines()
    inFile.close()
    lines = [line.replace('\n','') for line in lines]
    return lines

def verbs_present_in_text(text):
    verbs_detected = False
    try:
        tokens = nltk.word_tokenize(text) # using "text.lower" instead of "text" reduces accuracy
        text = nltk.Text(tokens)
        tags = nltk.pos_tag(text)
        for item in tags:
            verb_types = ['VBD','VBN','VB','VBG','VBP','VBZ'] # see tag decoder here: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
            #VBG and VBD are OK. VBD (verbs, past tense) mistakes same names ending in "ed" (Ted, Fred) for verbs unfortunately
            # can reduce false positive rate by manually including some commonly mentioned names from the dataset in a list below (esp. names ending in -ed, and -ing):
            false_positivies = ['Managing','Hans','Zimmer','Chaves','Farkas','Ling','Bing','Wilfred','Jared','Ted','Fred','Olmsted','Blake','Rosalind','Zises','Irving','Dishing','King','Flink','Weiss','Loeing','gala','Lansing','Farhad','Fanning','Yves','Dolores','Delores','Barnet','Lazar','du','Ming','Khaled','Jennifer','Boujaran','Eeling','Leviant','Ning','Lady','Krasting','Yanartag','Rashad','Yuqing','Arend','Browning','Wright','Daize','Trish','Love','Loring','Seyfried','Proctor','Cotton','Ping','Obed','Rose','Hielmart','Wing','Estes','Dobbins','Fleming','Sting','Crutchfield','Guoqing','Graves','Jing','Ching','Ryman','Harned','Hartling','Redgrave','Stirling','Xiaoning','Monling','Arnett','Fielding']
            if item[1] in verb_types:
                if not (item[0] in false_positivies):
                    verbs_detected = True
    except:
        None #cant decode, skip
    return verbs_detected

def final_filtering():
    init_captions = load_file_as_list('captions.txt')
    print 'init len %i' %len(init_captions)

    i=0
    thing = "Click here for NYSD Contents\n"
    while thing in init_captions:
        i += 1
        init_captions.remove(thing)
    print 'without click here for NYSD contents %i' %len(init_captions)

    captions=[]
    i=0
    for line in init_captions:
        if line[0:14] != "Photographs by" and ("Click to order" not in line) and ("click to order" not in line):
            captions.append(line)
        else:
            i += 1
            
    print '... and without Photohraphs by %i' %len(captions)

    verblines = 0
    for line in captions:
        if verbs_present_in_text(line):
            verblines += 1
            captions.remove(line)
    return captions

def connector_fix():
    captions=final_filtering() 
    print 'without verbs (loaded) %i' %len(captions)

    for index, line in enumerate(captions):
        tout = re.search(':(.*)', line )
        if tout is not None:
            if len(tout.group(1)) > 3:
                captions[index] = tout.group(1)
            else:
                captions.remove(line)

    print 'filtering all connectors'
    for index,line in enumerate(captions): 
        connectors=[', and ',' and ',': ',',, ',' with '] #not incl comma or EOL
        to_remove=['Dr.',', MD',', M.D.',' MD',', PhD',', Ph.D.',' PhD',', Phd',' Phd',' DMD',', CEO',' CEO','CEO ']
        for el in connectors:
            if el in line:
                captions[index] = captions[index].replace(el,', ')
        for el in to_remove:
            if el in line:
                captions[index] = captions[index].replace(el,'')                                           
    return captions

captions = connector_fix()
people_by_captions = list(map(lambda s: s.split(', '), captions))
for caption in people_by_captions:
    if len(caption) == 2:
        temp0 = caption[0].split()
        if len(temp0) == 1:
            temp1 = caption[1].split()
            if len(temp1) == 2:
                caption[0] = caption[0] + " " + temp1[1]
    for perind, person in enumerate(caption):
        bloomberg_personas = ['Michael R. Bloomberg', 'Michael Bloomberg', 'former Mayor Michael Bloomberg', 'Mayor Michael Bloomberg', 'Mayor Michael R. Bloomberg','Mayor Bloomberg','Bloomberg','Bloomberg table','Bloomberg table.']
        fake_personas = ['MD','Mr.','Mrs.','PhD','Phd','Ph.D','Jr.','Sr.','friend','friends','President','children', 'Guest','his wife','a friend','family','guests','John','David','Peter','Susan']
        if person in bloomberg_personas:
            caption[perind] = 'Michael Bloomberg'
        if (person == 'Mr.') and (caption[perind+1].split()[0] == 'Mrs.'):
            mrssplit = caption[perind+1].split()[1:]
            caption[perind] = ' '.join(mrssplit)
            caption[perind+1] = ' '.join(['Mrs.',' '.join(mrssplit[1:])])
        if (person in fake_personas) and (person in caption):
            caption.remove(person)
        if len(person) == 0:
            caption.remove(person)
        else:
            if person[0] == " ":
                temp = caption[perind]
                caption[perind] = temp[1:]

#Graph:

unique_personas=[]
G=nx.Graph() #creates an empty graph with no nodes and no edges
for caption in people_by_captions:
    for index,person in enumerate(caption):
        if not (person in unique_personas):
            G.add_node(person)
            unique_personas.append(person)
            
    if len(caption)!=1: #don't account for anything without connections
        edge_pairs=[]
        count=0
        for gind1 in range(0,len(caption)):
            for gind2 in range(gind1+1,len(caption)):
                if not G.has_edge(caption[gind1],caption[gind2]):
                    G.add_edge(caption[gind1],caption[gind2],weight=1)
                    
                else:
                    G.edge[caption[gind1]][caption[gind2]]['weight'] += 1

print 'Number of unique personas detected %i' %len(unique_personas)

weighed_nodes=sorted(G.degree_iter(weight='weight'),key=itemgetter(1),reverse=True)
q1_ans=weighed_nodes[0:100] # need only top 100 nodes
write_list_to_file('top100_nodes_q1.txt', q1_ans)

weighed_edges=sorted(G.edges_iter(data=True),key=itemgetter(2),reverse=True)
q3_ans=weighed_edges[0:100]
write_list_to_file('top100_edges_q3.txt', q3_ans)

print 'top 100 pagerank entries:'
pg_result=nx.pagerank(G)
top_pg_entries = sorted(pg_result.iteritems(), key=itemgetter(1), reverse=True)[:100]
q2_ans = top_pg_entries
write_list_to_file('top100_pg_q2.txt', q2_ans)
