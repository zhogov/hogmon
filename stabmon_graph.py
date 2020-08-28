#!/usr/bin/env python3

import argparse
import time

import plotly.graph_objects as go
import plotly.subplots as subplots
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import webbrowser
import threading

# Default log file path. Can be set with --log argument
DEFAULT_LOG_FILE = 'stabmon.csv'

# Parse CLI arguments
parser = argparse.ArgumentParser(description='Draw graph based on CSV log file.')
parser.add_argument("--log", help=f'Log file location, defaults to "{DEFAULT_LOG_FILE}"', default=DEFAULT_LOG_FILE)
args = parser.parse_args()


def graph():
    df = pd.read_csv(args.log)
    df.columns = ['time', 'cpu', 'cpu_proc_max', 'mem', 'mem_proc_max', "latency", "net_error"]

    fig = subplots.make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["cpu"],
        hovertext=df["cpu_proc_max"],
        name="CPU usage % out of 100"
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["mem"],
        hovertext=df["mem_proc_max"],
        name="Mem usage %"
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["latency"],
        hovertext=df["net_error"],
        name="latency"
    ), secondary_y=True)

    fig.update_yaxes(range=[0, 100], secondary_y=False, title="CPU and memory, %")
    fig.update_yaxes(range=[0, 5000], secondary_y=True, title="Latency, ms")

    # Make chart legend horizontal
    fig.update_layout(legend=dict(orientation="h"))

    return fig


def serve_layout():
    return html.Div([
        dcc.Graph(figure=graph(), style={"height": "80vh"})
    ])


def open_browser():
    # Wait for server to start and open browser
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8050/")


if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app = dash.Dash()
    app.layout = serve_layout
    app.run_server(debug=True)
