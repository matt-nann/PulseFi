
from flask import Flask
import dash
from dash import dcc, html
import pandas as pd
import plotly.graph_objs as go
from flask import redirect, url_for, make_response

def add_dash_routes(app, db, spotify_and_fitbit_authorized_required):

    @app.route('/basicHeartRateAndTempo', methods=['GET'])
    @spotify_and_fitbit_authorized_required
    def basicHeartRateAndTempo():
        df_heartRate = app.fitbit_API.heartRateData()
        df_recentlyPlayed = app.spotify_API.getRecentlyPlayedWithFeatures()

        traces = []
        for index, row in df_recentlyPlayed.iterrows():
            # print(row)
            start_time = row['played_at']
            # print(start_time, type(start_time), row['duration_ms'], type(row['duration_ms']))
            end_time =  pd.to_datetime(start_time) + pd.Timedelta(milliseconds=row['duration_ms'][0])
            y_value = row['tempo']
            traces.append(go.Scatter(
                x=[start_time, end_time],
                y=[y_value, y_value],
                mode='lines',
                fill='tozeroy',
                showlegend=False
            ))

        layout = go.Layout(
            xaxis=dict(title='Time'),
            yaxis=dict(title='Tempo'),
            title="User's Heart Rate and Recently Played Music's Tempo"
        )

        fig = go.Figure(data=traces, layout=layout)
        fig.add_trace(go.Scatter(x=df_heartRate['datetime'], y=df_heartRate['bpm'], name='Heart Rate', marker=dict(color='blue')))

        return fig.to_html()


    # dashApp = dash.Dash(__name__, server=app, url_base_pathname='/dash/')

    # # Define routes for serving the graphs
    # @dashApp.server.route('/graph1')
    # @spotify_and_fitbit_authorized_required
    # def serve_graph1():
    #     df_heartRate = app.fitbit_API.heartRateData()
    #     if df_heartRate is None:
    #         return redirect(url_for('authorize_fitbit'))
    #     graph1_layout = html.Div([
    #         html.H1('Graph 1'),
    #         dcc.Graph(
    #             id='graph1',
    #             figure={
    #                 'data': [
    #                     {'x': df_heartRate['datetime'], 'y': df_heartRate['bpm'], 'type': 'line', 'name': 'Graph 1'},
    #                 ],
    #                 'layout': {
    #                     'title': 'Graph 1'
    #                 }
    #             }
    #         )
    #     ])
    #     return make_response(graph1_layout) #.to_html()

    # @dashApp.server.route('/graph2')
    # @spotify_and_fitbit_authorized_required
    # def serve_graph2():
    #     df_played = app.spotify_API.getRecentlyPlayedWithFeatures()
    #     if df_played is None:
    #         return redirect(url_for('authorize_spotify'))
    #     traces = []
    #     for index, row in df_played.iterrows():
    #         start_time = row['datetime']
    #         end_time = start_time + pd.Timedelta(milliseconds=row['duration_ms'])
    #         y_value = row['tempo']
    #         traces.append(go.Scatter(
    #             x=[start_time, end_time],
    #             y=[y_value, y_value],
    #             mode='lines',
    #             fill='tozeroy',
    #             showlegend=False
    #         ))

    #     # Create layout
    #     layout = go.Layout(
    #         xaxis=dict(
    #             title='Time'
    #         ),
    #         yaxis=dict(
    #             title='Tempo'
    #         )
    #     )
    #     fig = go.Figure(data=traces, layout=layout)
    #     graph2_layout = html.Div([
    #         html.H1('Graph 2'),
    #         dcc.Graph(
    #             id='graph2',
    #             figure=fig
    #         )
    #     ])

    #     return graph2_layout

    # # Define callback to update layout based on selected graph
    # @dashApp.callback(
    #     dash.dependencies.Output('app-content', 'children'),
    #     [dash.dependencies.Input('graph-dropdown', 'value')]
    # )
    # def display_graph(value):
    #     if value == 'graph1':
    #         return graph1_layout
    #     else:
    #         return graph2_layout

    # # set the layout to # create a temporary page

    # dashApp.layout = html.Div([
    #     dcc.Location(id='url', refresh=False),
    #     html.Div(id='page-content')
    # ])

    return app
