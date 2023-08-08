import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from datetime import date

df = pd.read_csv('/Users/jonathanguallasamin/Desktop/1.dashboards/datos_bancos3.csv')

df['fecha'] = pd.to_datetime(df['año'].astype(str) + '-' + df['mes'].astype(str), format='%Y-%m')

# Filtrar los datos desde 2022 Enero hasta 2023 Junio
start_date = pd.to_datetime('2022-01', format='%Y-%m')
end_date = pd.to_datetime('2023-06', format='%Y-%m')
df = df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Link(rel='stylesheet', href='/Users/jonathanguallasamin/Desktop/1.dashboards/assets/stylesheet.css'),
    html.H1('Indicadores de Morosidad', className='banner', style={'color': 'white', 'margin-top': '0px'}),

    html.Div([
        html.Div([
            html.P('Selecciona el Indicador', className='fix_label', style={'color': 'white', 'margin-top': '2px'}),
            dcc.RadioItems(
                options=[{'label': control, 'value': control} for control in df['NOMBRE DEL INDICADOR'].unique()],
                value='Morosidad de Cartera de Consumo',
                id='control',
                labelStyle={'display': 'inline-block'},
                style={'text-align': 'left', 'color': 'white'},
                className='dcc_compon'
            )
        ]),
        html.Div([
            dcc.DatePickerSingle(
                id='date',
                min_date_allowed=date(2022, 1, 1),
                max_date_allowed=date(2023, 6, 1),
                initial_visible_month=date(2022, 1, 1),
                date=date(2022, 1, 1),
                display_format='MMM YYYY'  # Formato para mostrar solo mes y año en el campo de entrada
            )
        ], className='create_container2 five columns', style={'margin-bottom': '20px'}),
    ], className='row flex-display'),

    html.Div([
        html.Div([
            html.P('Selecciona el banco', className='fix_label', style={'color': 'white', 'margin-top': '20px'}),
            dcc.Dropdown(
                options=[{'label': col, 'value': col} for col in df['variable'].unique()],
                value='BP GUAYAQUIL',
                id='c1'
            )
        ], style={'margin-bottom': '20px'}),
    ], className='row flex-display'),

    html.Div([
        html.Div([
            dcc.Graph(id="g1", figure={})
        ], className='create_container2 five columns', style={'background-color': 'rgba(0, 0, 0, 0)'}),

        html.Div([
            dash_table.DataTable(
                data=df.to_dict('records'),
                id="tab",
                columns=[
                    {'name': col, 'id': col, 'deletable': False, 'selectable': False} for col in df.columns if col != 'fecha'
                ],
                page_size=10,
                style_table={'overflowX': 'auto', 'color': 'white'},
                style_cell={'textAlign': 'left', 'backgroundColor': 'rgba(0, 0, 0, 0)'},
                style_data={'whiteSpace': 'normal'},
                style_header={'backgroundColor': 'rgba(0, 0, 0, 0)', 'fontWeight': 'bold'},
                style_data_conditional=[{'if': {'column_id': 'value'}, 'type': 'numeric', 'format': {'specifier': '.2f'}}
                ],
                sort_action='native',  # Allow native sorting
                style_as_list_view=True  # Agregar esta propiedad para hacer el fondo transparente
            )
        ], className='create_container2 five columns', style={'background-color': 'rgba(0, 0, 0, 0)'})
    ], className='row flex-display'),

        # Pie de página
    html.Div([
        html.P('© 2023 - Todos los derechos reservados', className='footer')
    ], className='footer-container')
], id='mainContainer', style={'display': 'flex', 'flex-direction': 'column'})

@app.callback(
    Output('g1', 'figure'),
    [Input('c1', 'value'),
     Input('control', 'value')]
)
def update_graph(selected_variable, control_value):
    dff = df[(df['variable'] == selected_variable) & (df['NOMBRE DEL INDICADOR'] == control_value)]

    fig = px.line(dff, x='fecha', y='value', title=f'{control_value} en {selected_variable}')

    # Agregar estilo para cambiar el color de la línea a blanco
    fig.update_traces(line=dict(color='white'))

    # Agregar estilo para cambiar el color del texto de la leyenda a blanco
    fig.update_layout(
        legend=dict(font=dict(color='white')),
        xaxis=dict(tickfont=dict(color='white')),  # Color de las leyendas del eje x
        yaxis=dict(tickfont=dict(color='white'))   # Color de las leyendas del eje y
    )

    # Eliminar las líneas de cuadrícula en el eje x y el eje y
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    # Agregar estilo para el título del gráfico
    fig.update_layout(title_font=dict(color='white'))

    return fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})


@app.callback(
    [Output('tab', 'data')],
    [Input('date', 'date'),
    Input('control', 'value')],
    [State('tab', 'sort_by')]
)
def update_table_data(selected_date, control_value, sort_by):
    dff = df[(df['NOMBRE DEL INDICADOR'] == control_value)]

    if selected_date:
        selected_date = pd.to_datetime(selected_date)
        dff = dff[dff['fecha'] == selected_date]

    if sort_by:
        for col, asc in sort_by:
            dff = dff.sort_values(col, ascending=asc)

    dff = dff.sort_values('value', ascending=False)

    return [dff.to_dict('records')]

if __name__ == '__main__':
    app.run_server(debug=True)
