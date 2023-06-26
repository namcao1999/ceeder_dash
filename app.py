import pandas as pd
from dash import Dash, Input, Output, dcc, html
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, "ELDs_result.xlsx")

data = (
    pd.read_excel(data_path)
    .assign(Date=lambda data: pd.to_datetime(data["Date"], format="%Y-%m-%d"))
    .sort_values(by="Date")
)
entities = data["Entity"].sort_values().unique()
products = data["Product"].sort_values().unique()

external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]


app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Exchange Analytics"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Img(src=app.get_asset_url('favicon.ico'), className="header-emoji"),
                html.Div(
                    children=[
                        html.H1(
                            children="ELDs Performance Analytics",
                            className="header-title"
                        ),
                        html.P(
                            children=(
                                "Analyze the performance of your entity"
                            ),
                            className="header-description",
                        ),
                    ],
                    className="header-content",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Entity", className="menu-title"),
                        dcc.Dropdown(
                            id="entity-filter",
                            options=[
                                {"label": entity, "value": entity}
                                for entity in entities
                            ],
                            value="VIETNAM",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Product", className="menu-title"),
                        dcc.Dropdown(
                            id="product-filter",
                            options=[
                                {
                                    "label": product.title(),
                                    "value": product,
                                }
                                for product in products
                            ],
                            value="oGV",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data["Date"].min().date(),
                            max_date_allowed=data["Date"].max().date(),
                            start_date=data["Date"].min().date(),
                            end_date=data["Date"].max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="approved-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="finished-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    Output("approved-chart", "figure"),
    Output("finished-chart", "figure"),
    Input("entity-filter", "value"),
    Input("product-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_charts(entity, product, start_date, end_date):
    filtered_data = data.query(
        "Entity == @entity and Product == @product"
        " and Date >= @start_date and Date <= @end_date"
    )
    approved_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["APPROVED"],  # Modify column name if needed
                "type": "lines",
                "hovertemplate": "%{x|%B %Y}: %{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": f"#{product} APPROVED of AIESEC in {entity} from {start_date} to {end_date}",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    finished_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["FINISHED"],  # Modify column name if needed
                "type": "lines",
                "hovertemplate": "%{x|%B %Y}: %{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": f"#{product} FINISHED of AIESEC in {entity} from {start_date} to {end_date}",
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return approved_chart_figure, finished_chart_figure


if __name__ == "__main__":
    server = app.server