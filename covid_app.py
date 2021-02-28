import pandas as pd
import dash
from jupyter_dash import JupyterDash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
from datetime import datetime as dt
import plotly.offline as py
import plotly.graph_objs as go

confirmed = pd.read_csv("Covid_confirmed.csv")

token = 'pk.eyJ1Ijoic2ltb25waG9lbml4IiwiYSI6ImNrbG5kbGpwcTBpMWIybmtkdjJ1YWZ3eXIifQ.F_PE3xPjy3asnN4Xc5hWag'

px.set_mapbox_access_token(token)

app = JupyterDash(__name__)

app.layout = html.Div(children = [
    html.H1("World Covid", style={'text-align': 'center'}),
    
    dcc.Dropdown(id="country-dropdown",
                 options=[{'label':i, 'value':i} 
                          for i in confirmed["country"].unique()],
                 multi=False,
                 value='Mexico',
                 style={'width': "40%"}
                 ),
    
    dcc.Dropdown(id="scale",
                 options=[{'label': 'Normal', 'value':'Normal'},
                         {'label': 'Logarithmic', 'value':'Logarithmic'}],
                 value='Normal',
                 style={'width': "40%"}
                 ),
    
    dcc.Graph(id='covid-graph', figure={}),
    
    html.H2("Pick a date and look at the maps", style={'text-align':'center'}),
    
    dcc.DatePickerSingle(id="my-date-picker-single",
                         min_date_allowed=dt(2020, 1, 22),
                         max_date_allowed=dt(2020, 10, 17),
                         initial_visible_month=dt(2020, 10, 17),
                         display_format='MMM Do, YYYY',
                         month_format='MMMM, YYYY',
                         day_size=43,
                         placeholder='Which Date?',
                         persistence=True,
                         date=dt(2020, 10, 17)),

    dcc.Graph(id="world-graph", figure={}),
    
    dcc.Graph(id='scatter_world_graph', figure={})
])

### setting the callback function
@app.callback(
    Output(component_id="covid-graph", component_property="figure"),
    [Input(component_id="country-dropdown", component_property="value"),
     Input(component_id="scale", component_property="value")]
)
def update_covid_graph(selected_country, scale):
    dff = confirmed.copy()
    dff = dff[dff['country'] == selected_country]
    if scale == 'Normal':
        fig = px.scatter(dff, x='date', y='confirmed', hover_data=['state'], labels={'date':'Date', 'confirmed':'Confirmed Cases'},
                        title="Covid Cases by Country").update_layout(font_family="Courier New",font_color="purple",title_font_family="Times New Roman",
                        title_font_color="blue", legend_title_font_color="green")
    else:
        fig = px.scatter(dff, x='date', y='confirmed', log_y=True, hover_data=['state'], labels={'date':'Date', 'confirmed':'Confirmed Cases'},
                        title="Covid Cases by Country").update_layout(font_family="Courier New",font_color="purple",title_font_family="Times New Roman",
                        title_font_color="blue", legend_title_font_color="green")    
    return fig

@app.callback(
    [Output(component_id="world-graph", component_property="figure"),
     Output(component_id="scatter_world_graph", component_property="figure")],
    Input(component_id="my-date-picker-single", component_property="date")
)
def update_world_graph(date_value):
    dff = confirmed.copy()
    dff['date'] = pd.to_datetime(dff["date"])
    dff = dff.loc[dff['date'] == date_value]
    
    fig = px.choropleth(dff, locations='country', locationmode='country names', color='confirmed').update_layout(height=500)
    fig2 = px.scatter_mapbox(dff, lat='lat', lon='long', size='confirmed', hover_name='country', hover_data=['state'], zoom=1,
                             color_discrete_sequence=["fuchsia"]).update_layout(mapbox_style="dark").update_layout(height=500)
    
    return fig, fig2

app.run_server(mode="jupyterlab", host = "localhost")