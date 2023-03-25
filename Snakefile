TRANS_BILLS_DIRECTORY = 'tmp/snakemake/trans_bills'
TRANS_METADATA_DIRECTORY = 'tmp/snakemake/trans_bills_metadata'
NEUTRAL_CORPUS_BILLS = 'tmp/snakemake/neutral_corpus_bills'
NEUTRAL_CORPUS_METADATA = 'tmp/snakemake/neutral_corpus_metadata'
NEUTRAL_CORPUS_ARCHIVE = 'tmp/snakemake/neutral_corpus_archive'

# https://edwards.flinders.edu.au/how-to-use-snakemake-checkpoints/
def get_bill_file_names(wildcards):
    ck_output = checkpoints.retrieve_legiscan_bills.get(**wildcards).output[0]
    MET, = glob_wildcards(os.path.join(ck_output, "{bill_name}"))
    return expand(os.path.join(ck_output, "{BILL_NAME}"), BILL_NAME=MET)

def get_neutral_bill_file_names(wildcards):
    ck_output = checkpoints.prepare_neutral_corpus.get(**wildcards).output[0]
    MET, = glob_wildcards(os.path.join(ck_output, "{bill_name}"))
    return expand(os.path.join(ck_output, "{BILL_NAME}"), BILL_NAME=MET)

def get_metadata_file_names(wildcards):
    ck_output = checkpoints.retrieve_legiscan_metadata.get(**wildcards).output[0]
    MET, = glob_wildcards(os.path.join(ck_output, "{bill_name}.json"))
    return expand(os.path.join(ck_output, "{BILL_NAME}.json"), BILL_NAME=MET)

def get_legiscan_archive_names(wildcards):
    ck_output = checkpoints.get_legiscan_archival_datasets.get(**wildcards).output[0]
    MET, = glob_wildcards(os.path.join(ck_output, "{bill_name}.zip"))
    return expand(os.path.join(ck_output, "{BILL_NAME}.zip"), BILL_NAME=MET)

def get_legiscan_archive_json_names(wildcards):
    ck_output = checkpoints.extract_legiscan_archival_datasets.get(**wildcards).output[0]
    MET, = glob_wildcards(os.path.join(ck_output, "{bill_name}.json"))
    MET2 = [met for met in MET if '/bill/' in met]
    return expand(os.path.join(ck_output, "{BILL_NAME}.json"), BILL_NAME=MET2)

rule _all:
    input:
        "static/visualize.html",
        "static/animated_choropleth.gif",
        "static/cloud-large.png",
        "static/dag.png"
        # get_bill_file_names
        # input: get_metadata_file_names

rule augment_legiscan_lookup:
    input:
        "tmp/snakemake/inferred_resolver_map.json",
        "tmp/snakemake/aclu_data.json"
    output:
        "tmp/snakemake/augmented_resolver_map.json"
    shell:
        """
        python lib/tasks/legiscan/augment_resolver_map.py \
            {input} {output}
        """

rule build_aggregate_dataset:
    input: get_metadata_file_names
    output:
        "tmp/snakemake/aggregate.json"
    shell:
        """
        python lib/tasks/build_aggregate_dataset.py {input} {output}
        """

rule build_legiscan_lookup:
    input:
        "tmp/snakemake/track_trans_legislation.json",
        "configuration/resolver_hints.json",
    output:
        "tmp/snakemake/inferred_resolver_map.json"
    shell:
        """
        python lib/tasks/legiscan/infer_resolver_map.py \
            {input} {output}
        """

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
        AGGREGATED_DATA_PATH=../{input[2]} \
        CATEGORIZED_PATH=../{input[3]} \
        jupyter nbconvert --stdout --execute --to html \
            {input[0]} > {output}
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
            {input} {output}
        """

checkpoint extract_legiscan_archival_datasets:
    input:
        get_legiscan_archive_names
    output:
        "tmp/snakemake/neutral_extract_done",
        directory(NEUTRAL_CORPUS_METADATA)
    shell:
        """
        mkdir -p {NEUTRAL_CORPUS_METADATA} && \
        python lib/tasks/extract_legiscan_datasets.py \
            {NEUTRAL_CORPUS_ARCHIVE} \
            {NEUTRAL_CORPUS_METADATA} && \
        touch tmp/snakemake/neutral_extract_done
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
            {input} {output}
        """

rule generate_word_cloud:
    input:
        "tmp/snakemake/bill_tokens.json",
        "tmp/snakemake/legal_stopwords.json"
    output:
        "static/cloud-large.png"
    shell:
        """
        python lib/tasks/visualization/generate_word_cloud.py \
            {input} \
            configuration/custom_stopwords.json \
            {output}
        """

checkpoint get_legiscan_archival_datasets:
    output:
        directory(NEUTRAL_CORPUS_ARCHIVE)
    shell:
        """
        mkdir -p {output} && \
        python lib/tasks/get_legiscan_datasets.py \
            {output}
        """

checkpoint prepare_neutral_corpus:
    input:
        "tmp/snakemake/neutral_summaries.json",
        "tmp/snakemake/aggregate.json",
    output:
        directory(NEUTRAL_CORPUS_BILLS)
    shell:
        """
        mkdir -p {NEUTRAL_CORPUS_BILLS} && \
        python lib/tasks/prepare_neutral_corpus.py \
            {input} {NEUTRAL_CORPUS_BILLS} && \
        touch tmp/snakemake/neutral_dataset_ready
        """

rule process_legiscan_archival_datasets:
    input:
        "tmp/snakemake/neutral_extract_done"
    output:
        "tmp/snakemake/neutral_summaries.json"
    shell:
        """
        python lib/tasks/process_legiscan_datasets.py \
            {NEUTRAL_CORPUS_METADATA} \
            {output}
        """

rule retrieve_aclu_dataset:
    output:
        "tmp/snakemake/aclu_data.json"
    shell:
        "python lib/tasks/retrieve_aclu_data.py {output}"

checkpoint retrieve_legiscan_bills:
    input:
        get_metadata_file_names,
    output:
        directory(TRANS_BILLS_DIRECTORY)
    shell:
        """
        mkdir -p {output} \
        && python lib/tasks/legiscan/retrieve_legislation.py \
            {input} {output}
        """

checkpoint retrieve_legiscan_metadata:
    output:
        directory(TRANS_METADATA_DIRECTORY)
    input:
        "tmp/snakemake/augmented_resolver_map.json"
    shell:
        """
        mkdir -p {output} && \
        python lib/tasks/legiscan/retrieve_metadata.py \
            {input[0]} \
            {output} \
        """

rule retrieve_ttl_dataset:
    output:
        "tmp/snakemake/track_trans_legislation.json"
    shell:
        "python lib/tasks/retrieve_ttl_data.py {output}"

rule select_legal_stopwords:
    input:
        "tmp/snakemake/neutral_tokens.json"
    output:
        "tmp/snakemake/legal_stopwords.json"
    shell:
        """
        python lib/tasks/prepare_legal_stopwords.py \
            {input} {output}
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

rule tokenize_neutral_corpus:
    input:
        get_neutral_bill_file_names,
    output:
        "tmp/snakemake/neutral_tokens.json"
    shell:
        """
        python lib/tasks/tokenize_bills.py {input} {output}
        """

rule visualize_workflow:
    input:
        "Snakefile"
    output:
        "static/dag.png"
    shell:
        "snakemake --forceall --rulegraph | dot -Tpng > static/dag.png"
