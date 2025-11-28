import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

def create_spatial_map(data: pd.DataFrame):
    pokemon_stores = data

    # Custom hover info
    customdata = pokemon_stores[['address']].values
    hovertemplate = (
        '<b>%{text}</b><br>' +
        'Address: %{customdata[0]}<br>' +
        '<extra></extra>'
    )

    # Create Plotly map
    fig = go.Figure()

    # Big red markers
    fig.add_trace(go.Scattermapbox(
        lat=pokemon_stores['lat'],
        lon=pokemon_stores['lon'],
        mode='markers',
        marker=dict(size=20, color='red', symbol='circle'),
        text=pokemon_stores['store_name'],
        customdata=customdata,
        hovertemplate=hovertemplate,
        name='Pokémon Stores'
    ))

    # Map center
    center_lat = pokemon_stores['lat'].mean()
    center_lon = pokemon_stores['lon'].mean()

    # Layout
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=center_lat, lon=center_lon),
            zoom=12
        ),
        margin=dict(l=0, r=0, t=0, b=0), 
        autosize=True
    )

    fig.update_layout(
        mapbox=dict(
            accesstoken=None,  
            zoom=12,
        ),
        dragmode='zoom'  
    )

    return fig