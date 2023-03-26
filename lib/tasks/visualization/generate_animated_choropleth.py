import io

from datetime import datetime
from itertools import product

import pandas as pd
import PIL
import plotly_express as px
import typer

from lib.util import load_json

def generate_animated_choropleth(
    aggregated_data_path: str,
    geography_data_path: str,
):
    """Generate an animated choropleth from the aggregated dataset"""
    aggregated = pd.read_json(aggregated_data_path)
    geography = load_json(geography_data_path)

    aggregated = aggregated.loc[aggregated.introduced_date > '2023-01-01'] # pylint: disable=E1101
    aggregated['introduced_date'] = (
        aggregated['introduced_date']
            .transform(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
    )

    all_dates = aggregated['introduced_date'].unique().tolist()
    all_states = geography['state_names'].keys()

    all_states_all_dates = pd.DataFrame(list(
        { 'state': tuple[0], 'introduced_date': tuple[1] }
        for tuple
        in product(all_states, all_dates)
    ))

    joined = (
        all_states_all_dates
        .set_index(['state', 'introduced_date'])
        .join(aggregated.set_index(['state', 'introduced_date']))
    )
    joined['ct'] = joined['bill_id'].apply(lambda x: 0 if pd.isnull(x) else 1)

    choropleth_data = (
        joined[['ct']]
        .reset_index()
        .groupby(by=['state', 'introduced_date'])
        .sum()
        .groupby(by='state')
        .cumsum()
        .reset_index()
    )

    national_data = choropleth_data.loc[choropleth_data.state == 'US']

    choropleth_data = (
        choropleth_data
        .set_index(['introduced_date'])
        .join(
            national_data
                .set_index(['introduced_date'])[['ct']]
                .rename(columns={'ct': 'national_ct'})
        )
        .reset_index()
    )

    choropleth_data['national_ct'] = choropleth_data['national_ct'] + choropleth_data['ct']
    choropleth_data = choropleth_data.rename(columns={'national_ct': 'ct_with_national'})

    fig = px.choropleth(
        choropleth_data,
        locations = 'state',
        color="ct_with_national",
        animation_frame="introduced_date",
        color_continuous_scale="reds",
        locationmode='USA-states',
        scope="usa",
        range_color=(
            0,
            (
                choropleth_data['ct'].mean()
                + choropleth_data['ct'].std() * 4
                + national_data['ct'].max()
            )
        ),
        title='Anti-Trans Bills by State',
        height=600
    )

    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 100
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 75

    fig.update_layout(
        height=600,
        width=1000,
        title_text = 'Anti-Trans Bills by State (2023)',
        title_font_size = 22,
        title_font_color="black",
        title_x=0.45,
    )

    return fig


def save_animated_choropleth(
    fig,
    output_path: str,
):
    """Make an animated GIF from the animated plot"""
    frames = []
    for slider, frame in enumerate(fig.frames):
        # set main traces to appropriate traces within plotly frame
        fig.update(data=frame.data)
        # move slider to correct place
        fig.layout.sliders[0].update(active=slider)
        # generate image of current state
        frames.append(PIL.Image.open(io.BytesIO(fig.to_image(format="png"))))

    # create animated GIF
    frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            duration=150,
            loop=0,
        )


def main(
    aggregated_data_path: str,
    geography_data_path: str,
    output_path: str,
):
    """The CLI for this task"""
    fig = generate_animated_choropleth(
        aggregated_data_path,
        geography_data_path,
    )

    save_animated_choropleth(fig, output_path)

if __name__ == "__main__":
    typer.run(main)
