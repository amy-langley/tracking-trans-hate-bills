import typer

from wordcloud import WordCloud

from lib.util import load_json

def generate_word_cloud(
    bill_tokens_path: str,
    legal_stopwords_path: str,
    custom_stopwords_path: str,
):
    """Generate a word cloud using the specified files"""
    bill_tokens = load_json(bill_tokens_path)

    stopwords = set(
        load_json(legal_stopwords_path)
        + load_json(custom_stopwords_path)
    )

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
    wordcloud_plot = generate_word_cloud(
        bill_tokens_path,
        legal_stopwords_path,
        custom_stopwords_path,
    )

    wordcloud_plot.to_file(output_path)

if __name__ == "__main__":
    typer.run(main)
