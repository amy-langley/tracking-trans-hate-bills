BILLS_DIRECTORY = 'tmp/snakemake/bills'
METADATA_DIRECTORY = 'tmp/snakemake/metadata'

# snakemake --forceall --rulegraph | dot -Tpng > dag.png

def get_bill_file_names(wildcards):
    # https://edwards.flinders.edu.au/how-to-use-snakemake-checkpoints/
    ck_output = checkpoints.retrieve_legiscan_bills.get(**wildcards).output[0]
    MET, = glob_wildcards(os.path.join(ck_output, "{bill_name}"))
    return expand(os.path.join(ck_output, "{BILL_NAME}"), BILL_NAME=MET)

def get_metadata_file_names(wildcards):
    # https://edwards.flinders.edu.au/how-to-use-snakemake-checkpoints/
    ck_output = checkpoints.retrieve_legiscan_metadata.get(**wildcards).output[0]
    MET, = glob_wildcards(os.path.join(ck_output, "{bill_name}.json"))
    return expand(os.path.join(ck_output, "{BILL_NAME}.json"), BILL_NAME=MET)

rule all:
    input:
        "static/visualize.html",
        "static/animated_choropleth.gif",
        "static/cloud-large.png",
        "static/dag.png"
        # get_bill_file_names
        # input: get_metadata_file_names

rule build_visualization_notebook:
    input:
        "visualize/aggregate-short.ipynb",
        "datasets/geography.json",
        "tmp/snakemake/aggregate.json",
        "tmp/snakemake/categorized.json",
    output:
        "static/visualize.html"
    shell:
        """
        GEOGRAPHY_PATH=../{input[1]} \
        AGGREGATE_PATH=../{input[2]} \
        CATEGORIZED_PATH=../{input[3]} \
        jupyter nbconvert --stdout --execute --to html \
            {input[0]} > {output}
        """

rule visualize_workflow:
    input:
        "Snakefile"
    output:
        "static/dag.png"
    shell:
        "snakemake --forceall --rulegraph | dot -Tpng > static/dag.png"

rule refresh_bill_lists:
    input:
        "tmp/snakemake/track_trans_legislation.json",
        "tmp/snakemake/aclu_data.json"

rule generate_word_cloud:
    input:
        "tmp/snakemake/bill_tokens.json"
    output:
        "static/cloud-large.png"
    shell:
        """
        python lib/tasks/visualization/generate_word_cloud.py \
            {input} \
            artifacts/legal_stopwords.json \
            configuration/custom_stopwords.json \
            {output}
        """

rule tokenize_bills:
    input:
        get_bill_file_names
    output:
        "tmp/snakemake/bill_tokens.json"
    shell:
        """
        python lib/tasks/tokenize_bills.py {input} {output}
        """

checkpoint retrieve_legiscan_bills:
    input:
        get_metadata_file_names,
    output:
        directory(BILLS_DIRECTORY)
    shell:
        """
        mkdir -p {output} \
        && python lib/tasks/legiscan/retrieve_legislation.py \
            {input} \
            {output}
        """

rule generate_animated_choropleth:
    input:
        "tmp/snakemake/aggregate.json",
        "datasets/geography.json"
    output:
        "static/animated_choropleth.gif"
    shell:
        """
        python lib/tasks/visualization/generate_animated_choropleth.py \
            {input} \
            {output}
        """

rule categorize_aggregate_dataset:
    input:
        "datasets/tracktranslegislation-meta.json",
        "tmp/snakemake/aggregate.json"
    output:
        "tmp/snakemake/categorized.json"
    shell:
        """
        python lib/tasks/categorize_aggregate_dataset.py \
            {input[0]} \
            {input[1]} \
            {output}
        """

rule build_aggregate_dataset:
    input: get_metadata_file_names
    output:
        "tmp/snakemake/aggregate.json"
    shell:
        """
        python lib/tasks/build_aggregate_dataset.py {input} {output}
        """

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
