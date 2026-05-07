import networkx as nx
import matplotlib.pyplot as plt

def add_with_weight(source,target,Graph):
    if Graph.has_edge(source,target):
        Graph.edges[(source,target)]["weight"] += 1
    else:
        Graph.add_edge(source,target,weight=1)

def create_DiGraph(users,tweets):
    G = nx.DiGraph()
    G.add_nodes_from(users.values())

    for tweet in tweets:
        user_node=tweet["author"]["user_id"] #source node
        
        #add edges for all the replies
        reply=tweet.get("inReplyToUserId") #target node
        if reply and G.has_node(reply):
            add_with_weight(user_node,reply,G)

        #add edges for all mentions
        mentions=tweet["user_mentions"] #target nodes
        for mention in mentions:
            if G.has_node(mention):
                add_with_weight(user_node,mention,G)
        
        #add edges from quotes
        quote=tweet.get("quoted_user_id") #target node
        if quote and G.has_node(quote):
            add_with_weight(user_node,quote,G)
    return G

def remove_selfloops(Graph):
    G_plot=Graph.copy()

    # Detect self-loop nodes before removing loops
    self_loop_nodes = set(u for u, v in nx.selfloop_edges(G_plot))

    # Remove self-loops from drawing
    G_plot.remove_edges_from(nx.selfloop_edges(G_plot))

    return G_plot,self_loop_nodes



def plot_graph(Graph,threshold,window):

    G_plot,self_loop_nodes=remove_selfloops(Graph)

    #remove isolated nodes, with degree less than threshold
    nodes_to_keep = [n for n in G_plot.nodes() if G_plot.degree(n) > threshold]

    G_plot = G_plot.subgraph(nodes_to_keep)
    
    print("Number of edges in figure: ",G_plot.number_of_edges())
    print("Number of nodes in figure: ",len(nodes_to_keep))
    
    # Layout
    pos = nx.spring_layout(G_plot, k=0.2, iterations=50, seed=42)

    # Degree-based sizes
    degrees = dict(G_plot.degree())

    node_sizes = [
        20 + degrees[n] * 8   # base size + scaling
        for n in G_plot.nodes()
    ]

    # Color nodes with self-loops differently
    node_colors = [
        'orange' if n in self_loop_nodes else 'steelblue'
        for n in G_plot.nodes()
    ]

    plt.figure(figsize=(window, window))

    nx.draw_networkx_nodes(
        G_plot,
        pos,
        node_size=node_sizes,
        node_color=node_colors,
        alpha=0.8
    )

    nx.draw_networkx_edges(
        G_plot,
        pos,
        arrows=True,
        arrowsize=4,
        width=0.3,
        alpha=0.3
    )

    plt.axis('off')
    plt.show()


def plot_largest_weak(Graph):
    largest_cc = max(nx.weakly_connected_components(Graph), key=len)
    subgraph = Graph.subgraph(largest_cc).copy()
    plot_graph(subgraph,0,12)

def plot_largest_strong(Graph):
    largest_cc = max(nx.strongly_connected_components(Graph), key=len)
    subgraph = Graph.subgraph(largest_cc).copy()
    plot_graph(subgraph,0,12)


def get_graph_features(Graph):
    #fix: the features may need some modification

    G_plot,self_loop_nodes=remove_selfloops(Graph)
    core=nx.core_number(G_plot)
    indegs=G_plot.in_degree()
    outdegs=G_plot.out_degree()
    weighted_indegs=G_plot.in_degree(weight="weight")
    weighted_outdegs=G_plot.out_degree(weight="weight")

    degrees=[indegs,outdegs,weighted_indegs,weighted_outdegs]

    #for the measures below, sel-loops were included
    betweenness=nx.betweenness_centrality(Graph, normalized=False, endpoints=False)
    pagerank=nx.pagerank(Graph, alpha=0.85)
    clustering=nx.clustering(Graph)

    return [betweenness,pagerank,clustering,core, self_loop_nodes],degrees


def add_graph_features(G,tweet,features,degrees):
    user_id=tweet["author"].get("user_id")
    tweet["author"]["betweenness"]=features[0][user_id]
    tweet["author"]["pagerank"]=features[1][user_id]
    tweet["author"]["clustering"]=features[2][user_id]
    tweet["author"]["core"]=features[3][user_id]
    if user_id in features[4]:
        tweet["author"]["has_selfloop"]=True
        tweet["author"]["weight"] = G[user_id][user_id]["weight"] 
    else:
        tweet["author"]["has_selfloop"]=False
    
    tweet["author"]["indeg"]=degrees[0][user_id]
    tweet["author"]["outdeg"]=degrees[1][user_id]
    tweet["author"]["weighted_indeg"]=degrees[2][user_id]
    tweet["author"]["weighted_outdeg"]=degrees[3][user_id]

    return tweet