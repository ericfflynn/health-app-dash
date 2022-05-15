from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import numpy as np
import requests
#Data Pull

Response = requests.get('https://ericfflynn.github.io/Data/HealthAutoExport.json')
data = Response.json()

df = pd.DataFrame(data['data']['workouts'])
df.drop(['humidity','stepCadence','swimCadence','stepCount','totalSwimmingStrokeCount', \
       'heartRateRecovery', 'isIndoor', 'temperature', 'flightsClimbed','speed'],axis=1,inplace=True)
    
df['Start'] = pd.to_datetime(df['start']).apply(lambda x: x.date())
df['End'] = pd.to_datetime(df['end']).apply(lambda x: x.date())
df['Startstr'] = df['Start'].apply(lambda x: x.strftime('%Y-%m-%d'))
df['start'] = df['start'].apply(lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S %z"))
df['end'] = df['end'].apply(lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S %z"))
df['Duration'] = df['end']-df['start']
df['YearMonth'] = df['Start'].apply(lambda x: x.strftime("%m-%Y"))
df['YearWeek'] = df['start'].apply(lambda x: x.strftime("%Y-%W"))
for i in ['activeEnergy','avgHeartRate','maxHeartRate','distance','totalEnergy','intensity',]:
    df[i] = df[i].apply(lambda x: x['qty'])




row_1 = dbc.Row(
    dbc.CardBody(
        [
            html.H5("Workout KPI's", className="text-center"),
        ]
    ),
)

row_2 = dbc.Row(
    [
        dbc.Col(dbc.Card([
            dbc.CardHeader("Average Workouts Per Month",style={'textAlign':'center'}),
            dbc.CardBody(
                [html.H5(id="Avg_Workouts", className="card-title",style={'textAlign':'center'}),
                ]
            ),
        ], outline=False)),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Average Calories Per Workout",style={'textAlign':'center'}),
            dbc.CardBody(
                [html.H5(id='Avg_Cal', className="card-title",style={'textAlign':'center'}),
                ]
            ),
        ], outline=False)),
    ],
)


row_3 = dbc.Row(
    [
        dbc.Col(dbc.Card([
            dbc.CardHeader("Average BPM",style={'textAlign':'center'}),
             dbc.CardBody(
                [html.H5(id='Avg_BPM', className="card-title",style={'textAlign':'center'}),

                ]
            ),
        ], outline=False)),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Max BPM",style={'textAlign':'center'}),
            dbc.CardBody(
                [html.H5(id='Max_BPM', className="card-title",style={'textAlign':'center'}),
                ]
            ),
        ], outline=False)),
    ],
)

KPI_stack = html.Div([row_1, html.Br(), row_2, row_3])

Workout_stats = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Date"),
                    dcc.Dropdown(id='datedropdown',style={'width': '200px'},clearable=False),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Type"),
                    html.P(id='Type',
                    ),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Duration"),
                    html.Div(id='Duration',
                    ),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Active Cal"),
                    html.Div(id='Active_cal',
                    ),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5(id='single1'),
                    html.P(id='Avg_hr',
                    ),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Max HR"),
                    html.P(id='Max_hr',
                    ),
                ]
            )
        ),
    ],style={'textAlign':'center'}
)

Latest_Update = 'Latest Update: '+ df['Start'].iloc[0].strftime("%m/%d/%Y")

external_stylesheets = [dbc.themes.BOOTSTRAP]


app = Dash(__name__, external_stylesheets = external_stylesheets)

server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Eric Flynn's Personal Fitness Dashboard",className='header-title'
                ),
                 html.P(
                     children=Latest_Update, className='header-description',
                ),
            ],
            className='header',
        ),
          
        
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(children="Workout Type", className="menu-title", style={'textAlign':'center'}),
                    dcc.Dropdown(
                        id="type-filter",
                        options=[{'label': 'Select All', 'value': 'all_values'}] +
                        [{"label": workout_type, "value": workout_type}
                         for workout_type in ['Traditional Strength Training','Running','Cycling','Yoga', 'Walking','Tennis','Golf']
                        ], 
                        value='all_values',
                        clearable=False,
                        searchable=False,
                        className="dropdown",
                    ),
                ],
            ),
            html.Div(
                children=[
                    html.Div(
                        children="Date Range",
                        className="menu-title",
                        style={'textAlign':'center'}
                        ),
                    dcc.DatePickerRange(
                        id="date-range",
                        min_date_allowed=df.Start.min(),
                        max_date_allowed=df.Start.max(),
                        start_date=df.Start.min(),
                        end_date=df.Start.max(),
                    ),
                ]
            ),
        ],
        className="menu",
    ),
 
        
        html.Div([
            html.Br(),
            dbc.Row([
                dbc.Col(KPI_stack,width=4),
                dbc.Col(dcc.Graph(id='figb'))
                ]
            )
            ]   
        ),
        
        html.Br(),
        html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Single Workout Analysis",className='header-title'
                ),
                 html.P(
                     children='This section is designed to analyze individual workout heart rate data or GPS data when available', className='header-description',
                ),
            ],
            className='subheader',
            
        ),
    ],
        ),
        
        dbc.Card(Workout_stats),
        
        dcc.Graph(id='graph'),

    ]
)

@app.callback(
        Output('datedropdown','options'),
        Output('datedropdown','value'),
        Output("figb", "figure"),
        Output('Max_BPM','children'),
        Output('Avg_BPM','children'),
        Output('Avg_Cal','children'),
        Output('Avg_Workouts','children'),
        
        Input("type-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"))

def Update_charts_KPI(workout_type, start_date, end_date):
    if workout_type == 'all_values':    
        sdate = datetime.strptime(start_date,"%Y-%m-%d").date()
        edate = datetime.strptime(end_date,"%Y-%m-%d").date()
        mask = (
            (df.Start >= sdate)
            & (df.Start <= edate)
        )
        filtered_df = df.loc[mask, :]
        dim = pd.DataFrame(pd.date_range(sdate,edate-timedelta(days=1),freq='d')) 
        dim['YearMonth'] = dim[0].apply(lambda x: x.strftime("%m-%Y"))
        Dim_month = pd.DataFrame(list(np.unique(dim['YearMonth'])),columns=['Month'])
        Grouped = filtered_df.groupby(['YearMonth']).agg({'name':'count','activeEnergy':'sum','maxHeartRate':'max'}). \
        reset_index().rename(columns={'name':'# Workouts','activeEnergy':'Active Cal','maxHeartRate':'Max HR','YearMonth':'Month'})
        Monthly =  Dim_month.merge(Grouped,on='Month',how='left')
        Monthly['Date'] = Monthly['Month'].apply(lambda x: datetime.strptime(x,"%m-%Y").date())
        Monthly = Monthly.sort_values(by = ['Date'])
        Monthly = Monthly.reset_index(drop=True)
        Monthly['Avg Cal'] = Monthly['Active Cal'] / Monthly['# Workouts']
        Monthly.fillna(0,inplace=True)
        figb = px.bar(Monthly[-12:], x='Month', y='# Workouts',text_auto=True)
        figb.update_layout(
            yaxis={'visible': True, 'showticklabels': True, 'title':None,'showgrid':False},
            xaxis={'visible': True, 'showticklabels': True, 'title':None,'showgrid':False},
            title={'text':'Workouts Per Month','x':0.5,'y':0.9,'xanchor':'center','yanchor':'top'}
                          )
        figb.update_traces(marker_color='#079A82')
        Max_BPM = max(filtered_df['maxHeartRate'])
        Avg_BPM = '{:.0f}'.format(np.average(filtered_df['avgHeartRate']))
        Avg_Cal = '{:.0f}'.format(np.average(filtered_df['activeEnergy']))
        Avg_Workouts = '{:.1f}'.format(np.average(Monthly['# Workouts'].iloc[:-1]))
        return [{'label':i, 'value':i} for i in filtered_df['Startstr']], filtered_df['Startstr'].iloc[0], figb, Max_BPM, Avg_BPM, Avg_Cal, Avg_Workouts
    
    sdate = datetime.strptime(start_date,"%Y-%m-%d").date()
    edate = datetime.strptime(end_date,"%Y-%m-%d").date()
    mask = (
        (df.name == workout_type)
        & (df.Start >= sdate)
        & (df.Start <= edate)
    )
    filtered_df = df.loc[mask, :]
    dim = pd.DataFrame(pd.date_range(sdate,edate-timedelta(days=1),freq='d')) 
    dim['YearMonth'] = dim[0].apply(lambda x: x.strftime("%m-%Y"))
    Dim_month = pd.DataFrame(list(np.unique(dim['YearMonth'])),columns=['Month'])
    Grouped = filtered_df.groupby(['YearMonth']).agg({'name':'count','activeEnergy':'sum','maxHeartRate':'max'}). \
    reset_index().rename(columns={'name':'# Workouts','activeEnergy':'Active Cal','maxHeartRate':'Max HR','YearMonth':'Month'})
    Monthly =  Dim_month.merge(Grouped,on='Month',how='left')
    Monthly['Date'] = Monthly['Month'].apply(lambda x: datetime.strptime(x,"%m-%Y").date())
    Monthly = Monthly.sort_values(by = ['Date'])
    Monthly = Monthly.reset_index(drop=True)
    Monthly['Avg Cal'] = Monthly['Active Cal'] / Monthly['# Workouts']
    Monthly.fillna(0,inplace=True)
  
    figb = px.bar(Monthly[-12:], x='Month', y='# Workouts',text_auto=True)
    figb.update_layout(
        yaxis={'visible': True, 'showticklabels': True, 'title':None,'showgrid':False},
        xaxis={'visible': True, 'showticklabels': True, 'title':None,'showgrid':False},
        title={'text':'Workouts Per Month','x':0.5,'y':0.9,'xanchor':'center','yanchor':'top'}
                      )
    figb.update_traces(marker_color='#079A82')
    Max_BPM = max(filtered_df['maxHeartRate'])
    Avg_BPM = '{:.0f}'.format(np.average(filtered_df['avgHeartRate']))
    Avg_Cal = '{:.0f}'.format(np.average(filtered_df['activeEnergy']))
    Avg_Workouts = '{:.1f}'.format(np.average(Monthly['# Workouts'].iloc[:-1]))
    return [{'label':i, 'value':i} for i in filtered_df['Startstr']], filtered_df['Startstr'].iloc[0], figb, Max_BPM, Avg_BPM, Avg_Cal, Avg_Workouts



@app.callback(
    Output('Duration', 'children'),
    Output('Active_cal', 'children'),
    Output('Avg_hr', 'children'),
    Output('Max_hr', 'children'),
    Output('Type', 'children'),
    Output('single1', 'children'),
    Input('datedropdown', 'value'))

def update_workout_stats(date):
    Day_data = df.loc[df['Startstr'] == date].reset_index()
    Date = Day_data['Start'].iloc[0].strftime("%Y-%m-%d")
    Duration = str(Day_data['end'][0] - Day_data['start'][0])
    Active_cal = "{:,.0f}".format(Day_data['activeEnergy'][0])
    Avg_hr = "{:,.0f}".format(Day_data['avgHeartRate'][0])
    Max_hr = "{:,.0f}".format(Day_data['maxHeartRate'][0])
    Type = Day_data['name'][0]
    if Type in ['Running', 'Cycling', 'Walking']:
        Distance = float(Day_data['distance'].iloc[0])
        #Pace = ((Day_data['end'][0] - Day_data['start'][0])/timedelta(minutes=1))/Distance
        return Duration, Active_cal, "{:,.2f}".format(Distance), Max_hr, Type, 'Distance'

    else:
        return Duration, Active_cal, Avg_hr, Max_hr, Type, 'Avg HR'


@app.callback(
    Output('graph', 'figure'),
    Input('datedropdown', 'value'),
    Input('Type', 'children')
)

def update_figure(date, workout_type):
    Day_data = df.loc[df['Startstr'] == date].reset_index()
    if workout_type in ['Running', 'Cycling', 'Walking']:
        route = pd.DataFrame(Day_data['route'].loc[0])
        if len(route) > 0:
            route['timestamp'] = route['timestamp'].apply(lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S %z").strftime("%I:%M %p"))
            fig = px.scatter_mapbox(
                route, 
                lat="lat", 
                lon="lon",
                hover_name="timestamp",
                hover_data={
                    "lat": ":.2f",
                    "lon": ":.2f",
                    "altitude": ":.1f"
                },
                zoom=11, 
                height=500,
            )
            fig.update_layout(
                margin=dict(r=0, t=0, l=0, b=0),
                mapbox_style="white-bg",
                autosize = True,
                hovermode='closest',
                mapbox_layers=[
                    {
                        "below": 'traces',
                        "sourcetype": "raster",
                        "sourceattribution": "United States Geological Survey",
                        "source": [
                            "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                        ]
                    }
                  ]
            )
            return fig
        else:
            Heart_Rate = pd.DataFrame.from_dict(Day_data['heartRateData'][0])
            fig = px.line(x=Heart_Rate['date'],y=Heart_Rate['qty'])
            fig.update_layout(yaxis={'visible':True, 'title':'BPM'},
                              xaxis={'visible':False})
            fig.update_traces(line_color='#079A82')
            return fig
    else:
        Heart_Rate = pd.DataFrame.from_dict(Day_data['heartRateData'][0])
        fig = px.line(x=Heart_Rate['date'],y=Heart_Rate['qty'])
        fig.update_layout(yaxis={'visible':True, 'title':'BPM'},
                          xaxis={'visible':False})
        fig.update_traces(line_color='#079A82')
        return fig

if __name__ == '__main__':
    app.run_server(debug=True)
