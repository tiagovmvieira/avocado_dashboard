#import libraries
import dash
import pandas as pd
import numpy as np
import os

from dash import dcc
from dash import html
from dash.dependencies import Output, Input
from typing import List

WORKING_DIR = os.getcwd()

#data extraction
data = pd.read_csv(os.path.join(WORKING_DIR, 'resources/avocado.csv'))

#data preprocessing
data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d")
data.sort_values('Date', inplace = True)

#external stylesheets
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

#Dash class instantiation
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)
app.title = 'Advocado Analytics: Understand Your Avocados!'

#layout
app.layout = html.Div(
    children = [
        html.Div(
            children = [
                html.P(children = "🥑", className = "header-emoji"),
                html.H1(
                    children = "Avocado Analytics", className = "header-title"
                ),
                html.P(
                    children = "Analyze the behaviour of avocado prices"
                    " and the number of avocados sold in the US"
                    " between 2015 and 2018",
                    className = "header-description",
                ),
            ],
            className = "header",
        ),
        html.Div(
            children = [
                html.Div(
                    children = [
                        html.Div(children = "Region", className = "menu-title"),
                        dcc.Dropdown(
                            id = "region-filter", #identifier of the element
                            options = [
                                {"label": region, "value": region}
                                for region in np.sort(data.region.unique())
                            ], # options shown when the dropdown is selected. Expects a dict with labels and values.
                            value = 'Albany', # default value
                            clearable = False, # allows the user to leave this field empty if set to True
                            searchable = True, # whether to enable the searching feature or not.
                            className = 'dropdown', # class selector used for applying styles.
                        ),
                    ]
                ),
                html.Div(
                    children = [
                        html.Div(children = 'Type', className = 'menu-title'),
                        dcc.Dropdown(
                            id = "type-filter",
                            options = [
                                {"label": avocado_type, "value": avocado_type}
                                for avocado_type in data.type.unique()
                            ],
                            value = "organic", # default
                            clearable = False, # allows the user to leave this field empty if set to True
                            searchable = False, # whether to enable the searching feature or not
                            className = "dropdown", # class selector used for applying styles.
                        ),
                    ],
                ),
                html.Div(
                    children = [
                        html.Div(children = "Data Range", className = "menu-title"),
                        dcc.DatePickerRange(
                            id = "date-range",
                            min_date_allowed = data.Date.min().date(), # specifies the lowest selectable date for the component
                            max_date_allowed = data.Date.max().date(), # specifies the highest selectable date for the component
                            start_date = data.Date.min().date(), # specifies the starting date for the component
                            end_date = data.Date.max().date(), # specifies the ending date for the component
                        ),
                    ]
                ),
            ],
            className = "menu",
        ),
        html.Div(
            children = [
                html.Div(
                    children = dcc.Graph(
                        id = "price-chart",
                        config = {"displayModeBar": False},
                    ),
                    className = "card",
                ),
                html.Div(
                    children = dcc.Graph(
                        id = "volume-chart",
                        config = {"displayModeBar": False},
                    ),
                    className = "card",
                ),
            ],
            className = "wrapper",
        ),
    ]
)

#interactivity
@app.callback(
    [
        Output("price-chart", "figure"),
        Output("volume-chart", "figure")
    ], #more than one output, thus it's allocated into a List
    [
        Input("region-filter", "value"), 
        Input("type-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ], #above note is also valid on the Input
)

def update_charts(region: str, avocado_type: str, start_date: str, end_date: str) -> List[dict]:
    mask = (
        (data.region == region)
        & (data.type == avocado_type)
        & (data.Date >= start_date)
        & (data.Date <= end_date)
    )

    filtered_data = data.loc[mask, :] #acesses all the columns of the row mask

    price_chart_figure = {
        "data": [
            {
                "x": filtered_data['Date'],
                "y": filtered_data['AveragePrice'],
                "type": "lines",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Average Price of Avocados",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {
                "tickprefix": "$", 
                "fixedrange": True
            },
            "colorway": ["#17B897"],
        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data['Date'],
                "y": filtered_data['Total Volume'],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {
                "text": "Avocados Sold",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return [price_chart_figure, volume_chart_figure]

if __name__ == '__main__':
    app.run_server(debug = True)
