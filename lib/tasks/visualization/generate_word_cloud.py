import typer

from wordcloud import WordCloud

from lib.language.types import TokenStream
from lib.util import load_json

def generate_word_cloud(
    bill_tokens: TokenStream,
    legal_stopwords_path: str,
    custom_stopwords_path: str,
):
    """Generate a word cloud using the specified tokens"""

    stopwords = set(
        load_json(legal_stopwords_path)
        + load_json(custom_stopwords_path)
    )

    # https://matplotlib.org/stable/tutorials/colors/colormaps.html
    #     supported values are 'Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r',
    #     'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r',
    #     'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r',
    #     'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r',
    #     'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r',
    #     'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg',
    #     'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag',
    #     'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow',
    #     'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r',
    #     'hot', 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r',
    #     'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r',
    #     'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'turbo', 'turbo_r', 'twilight', 'twilight_r',
    #     'twilight_shifted', 'twilight_shifted_r', 'viridis', 'viridis_r', 'winter', 'winter_r'

    wordcloud = WordCloud(
        width=2560,
        height=1440,
        random_state=1,
        background_color='white',
        colormap='viridis',
        collocations=True,
        collocation_threshold=10,
        stopwords=set(stopwords),
        max_words=5000,
        min_word_length=3,
        max_font_size=200,
        min_font_size=6,
        relative_scaling=0.8,
        prefer_horizontal=1,
    )

    return wordcloud.generate(' '.join(bill_tokens))

def main(
    bill_tokens_path: str,
    legal_stopwords_path: str,
    custom_stopwords_path: str,
    output_path: str,
):
    """The CLI for this task"""
    bill_tokens = load_json(bill_tokens_path)

    wordcloud_plot = generate_word_cloud(
        bill_tokens,
        legal_stopwords_path,
        custom_stopwords_path,
    )

    wordcloud_plot.to_file(output_path)

if __name__ == "__main__":
    typer.run(main)
