rule legiscan_lookup:
    input:
        "tmp/snakemake/aclu_data.json",
        "tmp/snakemake/track-trans-legislation.json"

rule aclu_dataset:
    output:
        "tmp/snakemake/aclu_data.json"
    shell:
        "python lib/aclu/retrieve_data.py tmp/snakemake/aclu_data.json"

rule ttl_dataset:
    output:
        "tmp/snakemake/track-trans-legislation.json"
    shell:
        "python lib/ttl/retrieve_data.py tmp/snakemake/track-trans-legislation.json"
