from SPARQLWrapper import SPARQLWrapper, JSON

sparql_endpoint="https://2407.biogateway.eu/sparql"

def data_processing(consulta): #Function to process data
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint

    # Initialize SPARQLWrapper
    sparql = SPARQLWrapper(endpoint_sparql)
    sparql.setQuery(consulta)
    sparql.setReturnFormat(JSON)
    
    #Query
    results = sparql.query().convert()
    
    # Process results
    processed_results = []
    for result in results['results']['bindings']:
        processed_result = {}
        for variable in result.keys():
            value = result[variable]['value']
            processed_result[variable] = value
        processed_results.append(processed_result)
    return processed_results 

def translate_chr(chromosome):
    ncbi_chromosome_ids = {
    "chr-1": "NC_000001.11",
    "chr-2": "NC_000002.12",
    "chr-3": "NC_000003.12",
    "chr-4": "NC_000004.12",
    "chr-5": "NC_000005.10",
    "chr-6": "NC_000006.12",
    "chr-7": "NC_000007.14",
    "chr-8": "NC_000008.11",
    "chr-9": "NC_000009.12",
    "chr-10": "NC_000010.11",
    "chr-11": "NC_000011.10",
    "chr-12": "NC_000012.12",
    "chr-13": "NC_000013.11",
    "chr-14": "NC_000014.9",
    "chr-15": "NC_000015.10",
    "chr-16": "NC_000016.10",
    "chr-17": "NC_000017.11",
    "chr-18": "NC_000018.10",
    "chr-19": "NC_000019.10",
    "chr-20": "NC_000020.11",
    "chr-21": "NC_000021.9",
    "chr-22": "NC_000022.11",
    "chr-X": "NC_000023.11",
    "chr-Y": "NC_000024.10",
    "mitochondrial" : "NC_012920.1"
    }
    # Check if the chromosome exists in the dictionary
    if chromosome in ncbi_chromosome_ids:
        return ncbi_chromosome_ids[chromosome]
    else:
        return "Invalid chromosome identifier."