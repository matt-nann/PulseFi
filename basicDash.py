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



def foo():

    import flask
    from flask import redirect, render_template, url_for
    import dash
    from dash import dcc, html

    server = flask.Flask(__name__)

    @server.route('/')
    def index():
        return 'Hello world'

    app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')
    app.config.suppress_callback_exceptions = False

    # Define your graphs here
    graphs = {
        'graph1': {'data': [{'x': [1, 2, 3], 'y': [1, 2, 3], 'type': 'scatter', 'mode': 'lines', 'line': {'width': 2}, 'name': 'Graph 1'}], 'layout': {'title': 'Graph 1'}},
        'graph2': {'data': [{'x': [1, 2, 3], 'y': [4, 5, 6], 'type': 'scatter', 'mode': 'lines', 'line': {'width': 2}, 'name': 'Graph 2'}], 'layout': {'title': 'Graph 2'}}
    }

    # # Define your Dash endpoints here
    # @app.callback(dash.dependencies.Output('graph-content', 'children'), [dash.dependencies.Input('graph-dropdown', 'value')])
    # def display_graph(value):
    #     if value == 'graph1':
    #         graph = dcc.Graph(id='graph1', figure=graphs['graph1'])
    #     elif value == 'graph2':
    #         graph = dcc.Graph(id='graph2', figure=graphs['graph2'])
    #     else:
    #         graph = html.Div('Select a graph')
    #     return graph
    # @app.server.route('/graph1')
    # def serve_graph1():
    #     print('serving graph1')
    #     graphs['graph1']['data'][0]['y'] = [8,6,4]
    #     return redirect(url_for('/dash/'))
    # @app.server.route('/graph2')
    # def serve_graph2():
    #     print('serving graph2')
    #     graphs['graph2']['data'][0]['y'] = [10,3,1]
    #     return  redirect(url_for('/dash/'))

    @app.callback(dash.dependencies.Output('graph-content', 'children'), [dash.dependencies.Input('graph-dropdown', 'value')])
    def display_graph(value):
        if value == 'graph1':
            graph = serve_graph1()
        elif value == 'graph2':
            graph = serve_graph2()
        else:
            graph = html.Div('Select a graph')
        return graph

    def serve_graph1():
        graph = dcc.Graph(
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization'
                }
            }
        )          
        return graph
    def serve_graph2():
        graph = dcc.Graph(
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization'
                }
            }
        )
        return graph

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


# Video:    [DatePickerRange - Python Dash Plotly](https://youtu.be/5uwxoxaPD8M)
# Docs:     [dcc.DatePickerRange](https://dash.plotly.com/dash-core-components/datepickerrange)
#           [plotly.express.density_mapbox](https://plotly.com/python-api-reference/generated/plotly.express.density_mapbox.html#plotly.express.density_mapbox)
from datetime import datetime as dt
import plotly.express as px
import dash                                     # pip install dash
from dash import dcc, html, Input, Output
import pandas as pd
# Data from NYC Open Data portal
df = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Dash%20Components/DatePickerRange/Sidewalk_Caf__Licenses_and_Applications.csv")
df['SUBMIT_DATE'] = pd.to_datetime(df['SUBMIT_DATE'])
df.set_index('SUBMIT_DATE', inplace=True)
print(df[:5][['BUSINESS_NAME', 'LATITUDE', 'LONGITUDE', 'APP_SQ_FT']])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    dcc.DatePickerRange(
        id='my-date-picker-range',  # ID to be used for callback
        calendar_orientation='horizontal',  # vertical or horizontal
        day_size=39,  # size of calendar image. Default is 39
        end_date_placeholder_text="Return",  # text that appears when no end date chosen
        with_portal=False,  # if True calendar will open in a full screen overlay portal
        first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
        reopen_calendar_on_clear=True,
        is_RTL=False,  # True or False for direction of calendar
        clearable=True,  # whether or not the user can clear the dropdown
        number_of_months_shown=1,  # number of months shown when calendar is open
        min_date_allowed=dt(2018, 1, 1),  # minimum date allowed on the DatePickerRange component
        max_date_allowed=dt(2020, 6, 20),  # maximum date allowed on the DatePickerRange component
        initial_visible_month=dt(2020, 5, 1),  # the month initially presented when the user opens the calendar
        start_date=dt(2018, 8, 7).date(),
        end_date=dt(2020, 5, 15).date(),
        display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
        month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
        minimum_nights=2,  # minimum number of days between start and end date

        persistence=True,
        persisted_props=['start_date'],
        persistence_type='session',  # session, local, or memory. Default is 'local'

        updatemode='singledate'  # singledate or bothdates. Determines when callback is triggered
    ),

    html.H3("Sidewalk Café Licenses and Applications", style={'textAlign': 'center'}),
    dcc.Graph(id='mymap')
])


@app.callback(
    Output('mymap', 'figure'),
    [Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date')]
)
def update_output(start_date, end_date):
    print("update_output, start_date: " + str(start_date))
    # print("Start date: " + start_date)
    # print("End date: " + end_date)
    dff = df.loc[start_date:end_date]
    # print(dff[:5])

    fig = px.density_mapbox(dff, lat='LATITUDE', lon='LONGITUDE', z='APP_SQ_FT', radius=13, zoom=10, height=650,
                            center=dict(lat=40.751418, lon=-73.963878), mapbox_style="carto-positron",
                            hover_data={'BUSINESS_NAME': True, 'LATITUDE': False, 'LONGITUDE': False,
                                        'APP_SQ_FT': True})
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)