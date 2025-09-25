from __future__ import annotations

from typing import List

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

from utils.gate_utils import sequence_to_bloch_path
from app.components import make_bloch_figure

app = Dash(__name__)
app.title = "Bloch Sphere Visualizer (Dash)"

app.layout = html.Div([
    html.H2("Bloch Sphere Visualizer (Dash)"),
    html.Div([
        html.Label("Gate sequence (comma-separated)"),
        dcc.Input(id="sequence", value="H, Rz(pi/2), H", type="text", style={"width": "60%"}),
        html.Label(" Backend ", style={"marginLeft": "12px"}),
        dcc.Dropdown(id="backend", options=[
            {"label": "Plotly", "value": "plotly"},
            {"label": "Plotly (Animated)", "value": "plotly-anim"},
        ], value="plotly", clearable=False, style={"width": "240px", "display": "inline-block"}),
    ], style={"marginBottom": "16px"}),
    dcc.Graph(id="bloch-graph"),
])


@app.callback(Output("bloch-graph", "figure"), [Input("sequence", "value"), Input("backend", "value")])
def update_graph(seq_text: str, backend: str) -> go.Figure:
    sequence: List[str] = [t.strip() for t in (seq_text or "").split(",") if t.strip()]
    path = sequence_to_bloch_path(sequence) if sequence else []
    fig = make_bloch_figure(path, backend=backend)
    return fig  # type: ignore


if __name__ == "__main__":
    app.run_server(host="127.0.0.1", port=8050, debug=False)
