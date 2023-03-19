from nltk import word_tokenize as tokenize_text
import re


def clean_text(text: str) -> str:
    no_entities = (
        text
            .replace('–', '-')
            .replace('—', '-')
            .replace('“', '"')
            .replace('”', '"')
            .replace('’', '\'')
    )  # remove annoying HTML entities and things like that
    
    resolve_hyphens = re.subn(
        r'([A-Za-z]+)\s*-\s*\n\s*(\d+\s*)?([A-Za-z]+)',
        r'\g<1>\g<3>\n',
        no_entities
    )[0]  # subn returns a tuple including number of matches
    
    return resolve_hyphens
