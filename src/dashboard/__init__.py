
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
            end_time =  pd.to_datetime(start_time) + pd.Timedelta(milliseconds=row['duration_ms'])
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

    return app
