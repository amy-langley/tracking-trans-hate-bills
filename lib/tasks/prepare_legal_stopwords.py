import json
from nltk import FreqDist
from typing import List

def prepare_legal_stopwords(token_path: str, output_filename: str, min_frequency: int=800) -> List[str]:
    with open(token_path, 'r') as f:
        canonicalized_tokens = json.load(f)

    distribution = FreqDist(canonicalized_tokens)
    
    stopwords = list(
        k
        for k, v
        in distribution.items()
        if v > min_frequency and len(k) > 1
    )
    
    with open(output_filename, 'w') as f:
        json.dump(stopwords, f, indent=2)
    
    return stopwords
