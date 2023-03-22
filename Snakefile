METADATA_DIRECTORY = 'tmp/snakemake/metadata'

def get_metadata_file_names(wildcards):
    # https://edwards.flinders.edu.au/how-to-use-snakemake-checkpoints/
    ck_output = checkpoints.retrieve_legiscan_metadata.get(**wildcards).output[0]
    MET, = glob_wildcards(os.path.join(ck_output, "{bill_name}.json"))
    return expand(os.path.join(ck_output, "{BILL_NAME}.json"), BILL_NAME=MET)

rule all:
    input: get_metadata_file_names
    # input: METADATA_DIRECTORY
    # input: "tmp/snakemake/finished.txt"

checkpoint retrieve_legiscan_metadata:
    output:
        directory(METADATA_DIRECTORY)
    input:
        "tmp/snakemake/augmented_resolver_map.json"
    shell:
        """
        mkdir -p {output} && \
        python lib/tasks/legiscan/retrieve_metadata.py \
            {input[0]} \
            {output} \
        """

rule augment_legiscan_lookup:
    output:
        "tmp/snakemake/augmented_resolver_map.json"
    input:
        "tmp/snakemake/inferred_resolver_map.json",
        "tmp/snakemake/aclu_data.json"
    shell:
        """
        python lib/tasks/legiscan/augment_resolver_map.py \
            {input[0]} \
            {input[1]} \
            {output}
        """

rule build_legiscan_lookup:
    output:
        "tmp/snakemake/inferred_resolver_map.json"
    input:
        "tmp/snakemake/track_trans_legislation.json",
        "configuration/resolver_hints.json",
        "tmp/snakemake/aclu_data.json"
    shell:
        """
        python lib/tasks/legiscan/infer_resolver_map.py \
            {input[0]} \
            {input[1]} \
            {output}
        """

rule retrieve_aclu_dataset:
    output:
        "tmp/snakemake/aclu_data.json"
    shell:
        "python lib/tasks/retrieve_aclu_data.py {output}"

rule retrieve_ttl_dataset:
    output:
        "tmp/snakemake/track_trans_legislation.json"
    shell:
        "python lib/tasks/retrieve_ttl_data.py {output}"
