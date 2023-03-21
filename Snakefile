rule augment_lookup:
    output:
        "tmp/snakemake/augmented_resolver_map.json"
    input:
        "tmp/snakemake/inferred_resolver_map.json",
        "tmp/snakemake/aclu_data.json"
    shell:
        """
        python lib/legiscan/legiscan.py \
            augment-resolver-map \
            tmp/snakemake/inferred_resolver_map.json \
            tmp/snakemake/aclu_data.json \
            tmp/snakemake/augmented_resolver_map.json
        """

rule legiscan_lookup:
    output:
        "tmp/snakemake/inferred_resolver_map.json"
    input:
        "tmp/snakemake/aclu_data.json",
        "tmp/snakemake/track_trans_legislation.json"
    shell:
        """
        python lib/legiscan/legiscan.py \
            infer-resolver-map \
            tmp/snakemake/track_trans_legislation.json \
            configuration/resolver_hints.json \
            tmp/snakemake/inferred_resolver_map.json
        """

rule aclu_dataset:
    output:
        "tmp/snakemake/aclu_data.json"
    shell:
        "python lib/aclu/retrieve_data.py tmp/snakemake/aclu_data.json"

rule ttl_dataset:
    output:
        "tmp/snakemake/track_trans_legislation.json"
    shell:
        "python lib/ttl/retrieve_data.py tmp/snakemake/track_trans_legislation.json"
