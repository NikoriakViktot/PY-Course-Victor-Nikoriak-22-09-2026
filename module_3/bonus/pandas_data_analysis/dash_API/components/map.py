import plotly.express as px
from data_utils import get_dataset


def create_food_map(commodity):

    df = get_dataset("food")

    dff = df[df["товар"] == commodity]

    fig = px.scatter_map(   # scatter_mapbox прибрано в Plotly 6+
        dff,
        lat="широта",
        lon="довгота",
        color="ціна",
        size="ціна",
        hover_name="ринок",
        zoom=5,
    )

    fig.update_layout(
        map_style="carto-darkmatter",
        template="plotly_dark"
    )

    return fig


