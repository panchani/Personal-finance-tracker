import dash 
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import datetime
import json
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

try:
    with open('transaction.json', 'r') as f:
        transactions=json.load(f)
except FileNotFoundError:
    transactions=[]

app.layout = dbc.Container([
    html.H1("Personal Finance Tracker", className="my-4"), 
    dbc.Card([
        dbc.CardBody([
            html.H4("Add Transaction"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(id="amount",
                              type="number",
                              placeholder="Amount"),
                ], width=3),
                dbc.Col([
                    dbc.Select(id="category",
                               options=[
                                   {"label":"Income",
                                    "value":"income"},
                                    {"label":"Expenses",
                                    "value":"expenses"},
                                    {"label":"Food",
                                    "value":"food"},
                                    {"label":"Transport",
                                    "value":"transport"},
                                    {"label":"Entertainment",
                                    "value":"entertainment"},
                                    {"label":"Bills",
                                    "value":"bills"},

                               ])
                ],width=3),
                dbc.Col([
                    dbc.Input(id="description",
                              placeholder="Description")
                ],width=4),
                dbc.Col([
                    dbc.Button("Add", id="add-btn",color="primary")
                ],width=2 ),
            ]),
        ])
    ],class_name="mb-4"),
    #row of charts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Spending by Category"),
                    dcc.Graph(id="category-pie")
                ])
            ])
        ],width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Monthly Overview"),
                    dcc.Graph(id="monthly-bar")
                ])
            ])
        ],width=6)
    ]),
    #Transactions table heading
    html.H4("Recent Transactions",className="mt-4"),
    html.Div(id="transactions-table"),
    dcc.Interval(id="interval-component", 
                 interval=5*1000,n_intervals=0)
])

# callback decorator to updates ui components
'''
dash apps are interactive- when the user clicks buttons, 
changes inputs, or something else happen, the app needs 
to update parts of the UI dynammically. this is done
through callbacks.
'''
@app.callback(
    [Output("transactions-table", "children"),
     Output("category-pie", "figure"),
     Output("monthly-bar","figure")],

    [Input("add-btn", "n_clicks"),
     Input("interval-component", "n_intervals")],

    [State("amount", "value"),
     State("category", "value"),
     State("description","value")]

)
def update_data(n_clicks, n_intervals, amount, category, description):
    ctx=dash.callback_context

    if ctx.triggered[0]["prop_id"]=="add-btn.n_clicks" and all([amount, category, description]):
        transactions.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": amount,
            "category":category,
            "description":description,
        })
        with open("transactions.json", "w") as f:
            json.dump(transactions,f)

    #convert the transactions to dataframe
    df=pd.DataFrame(transactions)

    if len(df)==0:
        return dash.no_update
    
    #create the pie chart
    pie_fig=px.pie(df, values="amount", names="category",
                    title="Spending by Category")
    
    df['date']=pd.to_datetime(df['date'])

    monthly=df.groupby([df['date'].dt.strftime("%Y-%m"),
                        'category'])['amount'].sum().reset_index()
    
    bar_fig=px.bar(monthly, x="date", y="amount", color="category",
                   title="Monthly Overview")
    
    #build the transaction table for latest 5 entries
    table=dbc.Table([
        html.Thead(html.Tr([html.Th(col) for col in
                            ["Date", "Amount", "Category", 
                             "Description"]])),
        html.Tbody([
            html.Tr([
                html.Td(row["date"]),
                html.Td(f"${row['amount']:.2f}"),
                html.Td(row["category"]),
                html.Td(row["description"]),
            ]) for row in reversed(transactions[-5:])
        ])
    ], striped=True, bordered=True)
    return table, pie_fig, bar_fig




#run the dash server
if __name__== "__main__":
    app.run(debug='True', port=8050)


