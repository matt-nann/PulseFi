from flask import Flask, session
from datetime import datetime as dt
import json
import dash
from dash import dcc, html
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output

# TODO need a system to perodically remove data?
DATA_CACHE = {}

def add_dash_routes(app, db, spotify_and_fitbit_authorized_required):

    dashApp = dash.Dash(__name__, server=app, url_base_pathname='/dash/')
    dashApp.config.suppress_callback_exceptions = True

    dashApp.layout = html.Div([
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
            min_date_allowed=dt(2023, 4, 1),  # minimum date allowed on the DatePickerRange component
            max_date_allowed=dt.now().date(),  # maximum date allowed on the DatePickerRange component
            initial_visible_month=dt.now().date(),  # the month initially presented when the user opens the calendar
            start_date=dt.now().date() - pd.Timedelta(days=7),
            end_date=dt.now().date(),
            display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
            month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
            minimum_nights=2,  # minimum number of days between start and end date

            persistence=True,
            persisted_props=['start_date'],
            persistence_type='session',  # session, local, or memory. Default is 'local'

            updatemode='singledate'  # singledate or bothdates. Determines when callback is triggered
        ),
        dcc.Graph(id='heartRateGraph'),
        dcc.Graph(id='audioGraph')
    ])

    @spotify_and_fitbit_authorized_required
    def basicHeartRateAndTempo(df_heartRate, df_recentlyPlayed, df_ouraHeartRate):

        traces = []
        for index, row in df_recentlyPlayed.iterrows():
            start_time = row['played_at']
            # print(start_time, type(start_time), row['duration_ms'], type(row['duration_ms']))
            end_time =  pd.to_datetime(start_time) + pd.Timedelta(milliseconds=row['duration_ms'])
            y_value = row['tempo']
            traces.append(go.Scatter(
                x=[start_time, end_time],
                y=[y_value, y_value],
                mode='lines',
                fill='tozeroy',
                line=dict(width=2),
                showlegend=False
            ))

        layout = go.Layout(
            xaxis=dict(title='Time'),
            yaxis=dict(title='Tempo'),
            title="User's Heart Rate and Recently Played Music's Tempo",
            uirevision='true'
        )

        fig = go.Figure(data=traces, layout=layout)
        fig.add_trace(go.Scatter(x=df_heartRate['datetime'], y=df_heartRate['bpm'], name='Fitbit Heart Rate', marker=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df_ouraHeartRate['datetime'], y=df_ouraHeartRate['bpm'], name='Oura Heart Rate', marker=dict(color='red')))

        return fig

    @dashApp.callback(
        [Output('heartRateGraph', 'figure'), Output('audioGraph', 'figure')],
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date')]
    )
    def update_output(start_date, end_date):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        end_date = end_date + pd.Timedelta(hours=23, minutes=59)
        
        session_id = session.get('sid')
        # saving the heart rate and recently played data in the user's browser's cookies is unfeasibly because it's too much data
        if session_id not in DATA_CACHE:
            DATA_CACHE[session_id] = {}
        if 'df_heartRate' not in DATA_CACHE[session_id]:
            DATA_CACHE[session_id]['df_heartRate'] = app.fitbit_API.heartRateData()
        if 'df_recentlyPlayed' not in DATA_CACHE[session_id]:
            DATA_CACHE[session_id]['df_recentlyPlayed'] = app.spotify_API.getRecentlyPlayedWithFeatures()
        if 'df_ouraHeartRate' not in DATA_CACHE[session_id]:
            DATA_CACHE[session_id]['df_ouraHeartRate'] = app.oura_API.heartRate()
        df_heartRate = DATA_CACHE[session_id]['df_heartRate']
        df_recentlyPlayed = DATA_CACHE[session_id]['df_recentlyPlayed']
        df_ouraHeartRate = DATA_CACHE[session_id]['df_ouraHeartRate']

        dff_heartRate = df_heartRate[(df_heartRate['datetime'] >= start_date) & (df_heartRate['datetime'] <= end_date)]
        dff_recentlyPlayed = df_recentlyPlayed[(df_recentlyPlayed['played_at'] >= start_date) & (df_recentlyPlayed['played_at'] <= end_date)]
        dff_ouraHeartRate = df_ouraHeartRate[(df_ouraHeartRate['datetime'] >= start_date) & (df_ouraHeartRate['datetime'] <= end_date)]
        figHeartRate = basicHeartRateAndTempo(dff_heartRate, dff_recentlyPlayed, dff_ouraHeartRate)

        categories = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo']
        df_parallel = dff_recentlyPlayed[categories]
        fig_audio = px.parallel_coordinates(df_parallel, color='tempo')

        return figHeartRate, fig_audio

    return app