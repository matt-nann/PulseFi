# # # create Flask app
# # import os
# # from flask import Flask
# # from dash import Dash, dcc, html

# # app = Flask(__name__)

# # # define Flask endpoint
# # @app.route('/')
# # def index():
# #     return 'Hello Flask app'



# # dashApp = Dash(
# #     __name__,
# #     server=app,
# #     external_stylesheets=['/static/dist/css/style.css'],
# #     # external_scripts=external_scripts,
# #     routes_pathname_prefix='/dash/'
# # )

# # dashApp.layout = html.Div([
# #         dcc.Graph(
# #             id='example-graph',
# #             figure={
# #                 'data': [
# #                     {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
# #                     {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
# #                 ],
# #                 'layout': {
# #                     'title': 'Dash Data Visualization'
# #                 }
# #             }
# #         )
# #     ])
            
# # if __name__ == '__main__':
# #     dashApp.run_server(debug=True)

# import pandas as pd
# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output
# from flask import Flask, render_template

# # Create a Pandas DataFrame
# # load pickle
# import pickle
# import pandas as pd
# df = pd.read_pickle('data/df_heartRate.pkl')

# # Initialize the Dash app
# app = dash.Dash(__name__)

# # Define the layout of the app
# app.layout = html.Div([
#     dcc.Graph(id='my-graph'),
#     dcc.Dropdown(
#         id='column-dropdown',
#         options=[{'label': col, 'value': col} for col in df.columns],
#         value=df.columns[0]
#     )
# ])

# # Define the callback function that updates the graph when the dropdown value changes
# @app.callback(
#     Output('my-graph', 'figure'),
#     [Input('column-dropdown', 'value')]
# )
# def update_graph(column):
#     # Create the plot data
#     data = [
#         {'x': df.index, 'y': df[column], 'type': 'line', 'name': column}
#     ]
    
#     # Create the plot layout
#     layout = {
#         'title': column,
#         'xaxis': {'title': 'Index'},
#         'yaxis': {'title': column}
#     }
    
#     # Return the plot figure
#     return {'data': data, 'layout': layout}

# # Initialize the Flask app
# server = Flask(__name__)

# @server.route('/')
# def index():
#     return 'Hello Flask app'
# # Define an endpoint that renders the Dash app
# @server.route('/graph')
# def render_dash_app():
#     return render_template('my_dash_app.html', title='My Dash App')

# # Define the HTML template for the Dash app
# dash_template = '''
# <!DOCTYPE html>
# <html>
#     <head>
#         <title>{title}</title>
#         <script src="{{ url_for('static', filename='dash.js') }}"></script>
#         <link rel="stylesheet" href="{{ url_for('static', filename='dash.css') }}">
#     </head>
#     <body>
#         <div id="app-container">{%app_entry%}</div>
#         <footer>
#             {%config%}
#             {%scripts%}
#             {%renderer%}
#         </footer>
#     </body>
# </html>
# '''

# # Add the Dash app to the Flask app
# app.index_string = dash_template
# app.scripts.config.serve_locally = True
# app.css.config.serve_locally = True
# app.config.suppress_callback_exceptions = True

# # Run the app
# if __name__ == '__main__':
#     server.run(host='0.0.0.0',port=8080,threaded=True)

# from flask import Flask
# import dash
# from dash import dcc, html
# import pandas as pd

# # Initialize Flask server
# server = Flask(__name__)

# import pandas as pd
# df = pd.read_pickle('data/df_heartRate.pkl')

# # Initialize Dash app
# app = dash.Dash(__name__, server=server)

# # Define layout for first graph
# graph1_layout = html.Div([
#     html.H1('Graph 1'),
#     dcc.Graph(
#         id='graph1',
#         figure={
#             'data': [
#                 {'x': df['datetime'], 'y': df['value'], 'type': 'scatter', 'name': 'Graph 1'},
#             ],
#             'layout': {
#                 'title': 'Graph 1'
#             }
#         }
#     )
# ])

# # Define layout for second graph
# graph2_layout = html.Div([
#     html.H1('Graph 2'),
#     dcc.Graph(
#         id='graph2',
#         figure={
#             'data': [
#                 {'x': df['datetime'], 'y': 2 * df['value'], 'type': 'scatter', 'name': 'Graph 2'},
#             ],
#             'layout': {
#                 'title': 'Graph 2'
#             }
#         }
#     )
# ])

# # Define routes for serving the graphs
# @app.server.route('/graph1')
# def serve_graph1():
#     return app.index()

# @app.server.route('/graph2')
# def serve_graph2():
#     return app.index()

# # Define callback to update layout based on selected graph
# @app.callback(
#     dash.dependencies.Output('app-content', 'children'),
#     [dash.dependencies.Input('graph-dropdown', 'value')]
# )
# def display_graph(value):
#     if value == 'graph1':
#         return graph1_layout
#     else:
#         return graph2_layout

# # Define layout for app
# app.layout = html.Div([
#     html.H1('Dash Graph Selector'),
#     dcc.Dropdown(
#         id='graph-dropdown',
#         options=[
#             {'label': 'Graph 1', 'value': 'graph1'},
#             {'label': 'Graph 2', 'value': 'graph2'},
#         ],
#         value='graph1'
#     ),
#     html.Div(id='app-content')
# ])

# if __name__ == '__main__':
#     app.run_server(debug=True)




import flask
import dash
from dash import dcc, html

server = flask.Flask(__name__)

@server.route('/')
def index():
    return 'Hello world'

app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')
app.config.suppress_callback_exceptions = True

# Define your graphs here
graphs = {
    'graph1': {'data': [1, 2, 3], 'layout': {'title': 'Graph 1'}},
    'graph2': {'data': [4, 5, 6], 'layout': {'title': 'Graph 2'}}
}

# Define your Dash endpoints here
@app.callback(dash.dependencies.Output('graph-content', 'children'), [dash.dependencies.Input('graph-dropdown', 'value')])
def display_graph(value):
    if value == 'graph1':
        graph = dcc.Graph(id='graph1', figure=graphs['graph1'])
    elif value == 'graph2':
        graph = dcc.Graph(id='graph2', figure=graphs['graph2'])
    else:
        graph = html.Div('Select a graph')
    return graph

@app.server.route('/graph1')
def serve_graph1():
    graphs['graph1']['figure']['data'] = [7, 8, 9]
    return app.server.create_url('/dash')

@app.server.route('/graph2')
def serve_graph2():
    graphs['graph2']['figure']['data'] = [10, 11, 12]
    return app.server.create_url('/dash')

# Define your Dash layout here
app.layout = html.Div(children=[
    html.H1(children='Dash App'),
    dcc.Dropdown(
        id='graph-dropdown',
        options=[
            {'label': 'Graph 1', 'value': 'graph1'},
            {'label': 'Graph 2', 'value': 'graph2'}
        ],
        value='graph1'
    ),
    html.Div(id='graph-content')
])

if __name__ == '__main__':
    app.run_server(debug=True)
