import os
from typing import DefaultDict

from wtforms.validators import ValidationError
from forms import fileUploadForm

from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

import networkx as nx
from pyvis.network import Network
import pyvis
import pandas as pd
import matplotlib
#Import custom .py
import girvan_newman as gn
import louvain as lv


########################################################################################################


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/uploads'
app.config['SECRET_KEY'] = '593a3e75934d817316d4bcefa32859df'


ALLOWED_EXTENSIONS = {'csv'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def home():
    form = fileUploadForm()
    
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)

        # #File has .csv extension
        # if allowed_file(filename) :
        form.file.data.save(app.config['UPLOAD_FOLDER'] + '/' + filename)
        # else:
        #     raise ValidationError("El tipo de archivo debe ser .csv")
        
        # file_path = app.config['UPLOAD_FOLDER'] + '/' + request.args.get('name')
        # df = pd.read_csv(file_path)

        # #File is an edgelist
        # if df.columns.shape[0] != 2:
        #     raise ValidationError("El contenido del .csv debe ser una lista de aristas (nodo1, nodo2)")

        method = form.method.data
        return redirect(url_for('uploads', name=filename, method=method))

    return render_template('index.html', form=form)


def louvain(graph):
    supergraph, communities = lv.Louvain(graph)
    last_community = lv.last_community(graph, communities)
    modularity = nx.algorithms.community.quality.modularity(graph, lv.dendrogram(last_community))
    return last_community, modularity

def girvan_newman(graph):
    dendrogram, modularity = gn.Girvan_Newman_2004(graph)
    GN_communities = gn.dendrogram_to_community(dendrogram)
    return GN_communities, modularity


@app.route('/uploads/', methods = ['GET', 'POST'])
def uploads():
    file_path = app.config['UPLOAD_FOLDER'] + '/' + request.args.get('name')

    #Read .csv and check dataframe
    df = pd.read_csv(file_path)

    if len(df.columns) != 2:
        flash('File must be a .csv edgelist like : (source, target)')
        df = df.iloc[:,:2]

    #Generate graph
    df.columns = df.columns.str.lower()
    print(df.columns)

    graph = nx.from_pandas_edgelist(df, source=df.columns[0], target=df.columns[1]) 
    graph = graph.to_undirected(graph) # Unweighted undirected graph 

    #Retrieve method selected
    method = request.args.get('method')

    if (method == 'Louvain'):
        community, modularity = louvain(graph)

        # comms = DefaultDict(set)
        # for key, value in community.items():
        #     comms[value].add(key)
        # print(comms)

        print(modularity)

    elif (method == 'GirvanNewman'):
        community, modularity = girvan_newman(graph)
        print(modularity)
        print(community)

    else:
        flash('Method unknown or not supported')

    colors = get_community_colors(graph, community)
    degrees = dict(graph.degree)

    net = render_graph(df, colors, degrees)

    net.save_graph('./templates/graph.html')
    return render_template('uploads.html', title=request.args.get('name')[:-4] + ' ' + method)



def get_community_colors(graph, community):
	""" 
	Draws the graph using colors as community identifier
	"""
	num_comms = len(set(community.values()))
	cmap = matplotlib.cm.get_cmap('tab20', max(community.values()) + 1)
	norm = matplotlib.colors.Normalize(vmin=0, vmax=num_comms)
	colors = dict()

	for node in graph.nodes:
		colors.update({node:matplotlib.colors.rgb2hex(cmap(community[node]))})

	return colors



def render_graph(edge_list, colors, degrees):
    """
    Renders graph using pyvis.network
    Parameters:
        edge_list
        degrees: dict of nodes as keys and their degrees as values
        colors: dict of nodes as keys and their community color as hex values
    """
    #Setup net for representation
    net = Network(height='100%', width='100%', bgcolor='#222222', font_color='white', notebook=True)
    net.force_atlas_2based(overlap=0.7)
    net.repulsion(node_distance=200)  
    net.show_buttons(filter_=['physics'])

    sources = edge_list[edge_list.columns[0]]
    targets = edge_list[edge_list.columns[1]]

    edge_data = zip(sources, targets)

    for src, tar in edge_data:
        net.add_node(src, src, title=src, color=colors[src], size=degrees[src] )
        net.add_node(tar, tar, title=tar, color=colors[tar], size=degrees[tar] )
        net.add_edge(src, tar)

    return net


@app.route('/about')
def about():
    pass


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404_notfound.html')

if __name__ == '__main__':
    app.run(debug=True)

