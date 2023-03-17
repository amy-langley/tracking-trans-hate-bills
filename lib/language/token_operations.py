from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import re
import string

from .types import TaggedToken, TokenList, TokenStream, TaggedTokenStream


lem = WordNetLemmatizer()


def _get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def clean_tokens(token_stream: TokenStream) -> TokenStream:
    return (
        outer_token
        for outer_token
        in (
            token.lower().strip(string.punctuation)
            for token
            in token_stream
        )
        if (
            outer_token
            and outer_token not in string.punctuation
            and not re.search('\d', outer_token)
        )
    )

def retag_for_wordnet(tagged_token_stream: TaggedTokenStream) -> TaggedTokenStream:
    return (
        (word, _get_wordnet_pos(tag))
        for word, tag
        in tagged_token_stream
    )


# because POS tagging requires us to provide texts (so it can grab context),
# we have to eagerly evaluate the stream before canonicalizing
def canonicalize_tokens(token_list: TokenList) -> TokenStream:
    tagged = retag_for_wordnet(
        tagged_pair
        for tagged_pair
        in pos_tag(list(token_list))
    )

    return (
        lem.lemmatize(*tagpair)
        for tagpair
        in tagged
    )
