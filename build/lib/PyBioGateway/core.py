from SPARQLWrapper import SPARQLWrapper, JSON
from collections import defaultdict
from .utils import data_processing, translate_chr

sparql_endpoint= "https://2407.biogateway.eu/sparql"

def type_data(instance): 
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint

    # Check prefLabel
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT ?type ?graph
    WHERE {
        GRAPH ?graph {
            ?uri skos:prefLabel "%s" ;
                rdfs:subClassOf ?uri_type .
            ?uri_type skos:prefLabel ?type 
        }
    }
    """ % (instance)
    results = data_processing(query)
    
    if len(results) == 0:
        # Check altLabel
        query_alt_label = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT DISTINCT (REPLACE(str(?type), ".*?/", "") as ?type_id)
        WHERE {
            GRAPH ?graph {
                ?uri skos:altLabel "%s" ;
                    rdfs:subClassOf ?type .
            }
        }
        """ % (instance)
        results = data_processing(query_alt_label)
    
    if len(results) == 0:
        query_go = """
        PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
        SELECT DISTINCT ?type_id
        WHERE {
            GRAPH ?graph {
                ?uri obo:id "%s" ;
                obo:hasOBONamespace ?type_id .
            }
        }
        """ % (instance)
        results = data_processing(query_go)
    
    if results:
        first_result = results[0]
        type_id = first_result["type_id"]
        
        # Verificar si el tipo de ID comienza con "GO"
        if instance.startswith("GO"):
            return type_id
        else:
            # Agregar más lógica aquí según sea necesario para otros tipos de ID
            if type_id == "SO_0000727":
                return "cis_regulatory_module (crm)"
            elif type_id == "SIO_010035":
                return "gene"
            elif type_id == "SIO_010043":
                return "protein"
            elif type_id == "SO_0002304":
                return "topologically_associated_domain (tad)"     
            else:
                return "No data available for this instance"
    else:
        return "No data available for this instance"
    
def getGene_info(gene, taxon):
    if taxon.isdigit():
        # SPARQL query when taxon is provided as a number
        query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX gene: <http://rdf.biogateway.eu/gene/%s/>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX dc: <http://purl.org/dc/terms/>
        SELECT DISTINCT ?start ?end (REPLACE(STR(?strand), "http://biohackathon.org/resource/faldo#", "") AS ?strand) (REPLACE(STR(?chr), "https://www.ncbi.nlm.nih.gov/nuccore/", "") AS ?chr) (REPLACE(STR(?assembly), "https://www.ncbi.nlm.nih.gov/assembly/", "") AS ?assembly) (REPLACE(STR(?alt_gene_sources), "http://identifiers.org/", "") AS ?alt_gene_sources) ?definition
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/gene> {
              gene:%s  obo:GENO_0000894 ?start ;
                    obo:GENO_0000895 ?end ;
                    obo:BFO_0000050 ?chr ;
                    obo:GENO_0000906 ?strand ;
                    skos:definition ?definition ;
                    skos:closeMatch ?alt_gene_sources ;
                    dc:hasVersion ?assembly .
            }
        }
        """ % (taxon, gene)
        
        results = data_processing(query)
        
        if not results:
            return "No data available for the introduced gene or you may have introduced an instance that is not a gene. Check your data type with type_data function." 

        # Combine results into a single dictionary
        combined_result = {
            'start': results[0]['start'],
            'end': results[0]['end'],
            'strand': results[0]['strand'],
            'chr': results[0]['chr'],
            'assembly': results[0]['assembly'],
            'alt_gene_sources': [],
            'definition': results[0]['definition']
        }

        for result in results:
            alt_gene_sources = result['alt_gene_sources']
            if alt_gene_sources not in combined_result['alt_gene_sources']:
                combined_result['alt_gene_sources'].append(alt_gene_sources)

        combined_result['alt_gene_sources'] = '; '.join(combined_result['alt_gene_sources'])

        return combined_result
    else:
        # SPARQL query to get taxon URI when taxon is provided as a name
        query_tax = """
        PREFIX tax: <http://purl.obolibrary.org/obo/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?taxon WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/taxon> {
                ?taxon rdfs:label "%s".
            }
        }
        """ % taxon
        
        tax_result = data_processing(query_tax)
        
        if not tax_result:
            return "No data available for the introduced gene or you may have introduced an instance that is not a gene. Check your data type with type_data function." 

        tax_uri = tax_result[0]['taxon']  # Get the taxon URI from the query result
        num_taxon = tax_uri.split('_')[-1]  # Extract the taxon number from the URI
        
        query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX gene: <http://rdf.biogateway.eu/gene/%s/>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX dc: <http://purl.org/dc/terms/>
        SELECT DISTINCT ?start ?end (REPLACE(STR(?strand), "http://biohackathon.org/resource/faldo#", "") AS ?strand) (REPLACE(STR(?chr),    "https://www.ncbi.nlm.nih.gov/nuccore/", "") AS ?chr) (REPLACE(STR(?assembly), "https://www.ncbi.nlm.nih.gov/assembly/", "") AS ?assembly) (REPLACE(STR(?alt_gene_sources), "http://identifiers.org/", "") AS ?alt_gene_sources) ?definition
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/gene> {
              gene:%s  obo:GENO_0000894 ?start ;
                    obo:GENO_0000895 ?end ;
                    obo:BFO_0000050 ?chr ;
                    obo:GENO_0000906 ?strand ;
                    skos:definition ?definition ;
                    skos:closeMatch ?alt_gene_sources ;
                    dc:hasVersion ?assembly .
            }
        }
        """ % (num_taxon, gene)
        
        results = data_processing(query)
        
        if not results:
            return "No data available for the introduced gene or you may have introduced an instance that is not a gene. Check your data type with type_data function." 

        # Combine results into a single dictionary
        combined_result = {
            'start': results[0]['start'],
            'end': results[0]['end'],
            'strand': results[0]['strand'],
            'chr': results[0]['chr'],
            'assembly': results[0]['assembly'],
            'alt_gene_sources': [],
            'definition': results[0]['definition']
        }

        for result in results:
            alt_gene_sources = result['alt_gene_sources']
            if alt_gene_sources not in combined_result['alt_gene_sources']:
                combined_result['alt_gene_sources'].append(alt_gene_sources)

        combined_result['alt_gene_sources'] = '; '.join(combined_result['alt_gene_sources'])

        return combined_result
    
def getGenes_by_coord(chr, start, end , strand):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    
    # Construir la consulta SPARQL
    if strand==None:
        query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX nuccore: <https://www.ncbi.nlm.nih.gov/nuccore/>
        SELECT DISTINCT ?gene_name ?start ?end (REPLACE(STR(?strand), "http://biohackathon.org/resource/faldo#", "") AS ?strand) 
        WHERE {{
                GRAPH <http://rdf.biogateway.eu/graph/gene> {{
                    ?gene obo:GENO_0000894 ?start ;
                          skos:prefLabel ?gene_name ;
                          obo:GENO_0000895 ?end ;
                          obo:BFO_0000050 nuccore:%s ;
                          obo:GENO_0000906 ?strand ;
                          obo:RO_0002162 ?taxon .
                      # Filtrar por el cromosoma especificado
                  FILTER (xsd:integer(?start) >= %s && xsd:integer(?end) <= %s)
                }}
            }}
        """%(chr, start, end)
        results=data_processing(query)
        
    else:
        query_alt = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX nuccore: <https://www.ncbi.nlm.nih.gov/nuccore/>
        PREFIX strand: <http://biohackathon.org/resource/faldo#>
        SELECT DISTINCT ?gene_name ?start ?end 
        WHERE {{
                GRAPH <http://rdf.biogateway.eu/graph/gene> {{
                    ?gene obo:GENO_0000894 ?start ;
                          skos:prefLabel ?gene_name ;
                          obo:GENO_0000895 ?end ;
                          obo:BFO_0000050 nuccore:%s ;
                          obo:GENO_0000906 strand:%s;
                          obo:RO_0002162 ?taxon .
                      # Filtrar por el cromosoma especificado
                  FILTER (xsd:integer(?start) >= %s && xsd:integer(?end) <= %s)
                }}
            }}
        """%(chr, strand, start, end)
        results=data_processing(query_alt)
    if len(results)== 0:
        return "No data available for the introduced genomic coordinates."
    else:
        results_sorted = sorted(results, key=lambda x: x['gene_name'])

        return results_sorted

def getProtein_info(protein):
     # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    
    # Construir la consulta SPARQL
    query="""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX sch: <http://schema.org/>
    PREFIX sio: <http://semanticscience.org/resource/>
    SELECT DISTINCT ?protein_id ?protein_alt_id ?definition ?evidence_level (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) (REPLACE(STR(?alt_sources), "http://identifiers.org/", "") AS ?alt_sources)
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/prot> {
            ?prot skos:prefLabel "%s" ;
                  skos:altLabel ?protein_alt_id ;
                  skos:definition ?definition ;
                  sch:evidenceLevel ?evidence_level .
            OPTIONAL { ?prot sio:SIO_000772 ?articles. }
            OPTIONAL { ?prot skos:closeMatch ?alt_sources. }
        }
    }
    """ %(protein)
    results=data_processing(query)
    if len(results)== 0:
        return "No data available for the introduced protein or you may have introduced an instance that is not a protein. Check your data type with type_data function."
    else:
        combined_result = {
            'protein_alt_ids': [],
            'definition': results[0]['definition'],
            'evidence_level': results[0]['evidence_level'],
            'alt_sources': [],
            'articles': []
        }

        for result in results:
            alt_id = result['protein_alt_id']
            alt_sources=result['alt_sources']
            articles=result['articles']
            if alt_id not in combined_result['protein_alt_ids']:
                combined_result['protein_alt_ids'].append(alt_id)
            if alt_sources not in combined_result['alt_sources']:
                combined_result['alt_sources'].append(alt_sources)
            if articles not in combined_result['articles']:
                combined_result['articles'].append(articles)

        combined_result['protein_alt_ids'] = '; '.join(combined_result['protein_alt_ids'])
        combined_result['alt_sources'] = '; '.join(combined_result['alt_sources'])
        combined_result['articles'] = '; '.join(combined_result['articles'])
        return combined_result

def getPhenotype(phenotype):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    
    # Build the SPARQL query
    query = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT (REPLACE(STR(?omim_id), "http://purl.bioontology.org/ontology/OMIM/", "") AS ?omim_id) ?phen_label
    WHERE {{
        GRAPH <http://rdf.biogateway.eu/graph/omim> {{
            {{?omim_id skos:prefLabel ?phen_label}}
            UNION
            {{?omim_id skos:altLabel ?phen_label}}
        }}
        FILTER regex(?phen_label, "{phenotype}", "i")
    }}
    """
    
    results = data_processing(query)
    
    if len(results) == 0:
        if phenotype.isdigit() and len(phenotype) == 6 or phenotype.startswith("MTHU"):
            query_phen = """
            PREFIX omim: <http://purl.bioontology.org/ontology/OMIM/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT DISTINCT ?phen_label 
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/omim> {
                    omim:%s skos:prefLabel ?phen_label
                }
            }
            """ %(phenotype)

            results = data_processing(query_phen)
        else:
            return "No data available for the introduced phenotype or you may have introduced an instance that is not a phenotype. Check your data type with type_data function."
    results_sorted = sorted(results, key=lambda x: x['phen_label'])        
    return results_sorted

def getCRM_info(crm):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    
    # Construir la consulta SPARQL
    query="""
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX dc: <http://purl.org/dc/terms/>
    PREFIX sio: <http://semanticscience.org/resource/>
    SELECT DISTINCT ?start ?end (REPLACE(STR(?chr), "https://www.ncbi.nlm.nih.gov/nuccore/", "") AS ?chromosome) (REPLACE(STR(?assembly), "https://www.ncbi.nlm.nih.gov/assembly/", "") AS ?assembly) (REPLACE(STR(?taxon), "http://purl.obolibrary.org/obo/", "") AS ?taxon)  ?definition
     WHERE {
     GRAPH <http://rdf.biogateway.eu/graph/crm> { 
               ?enh_id skos:prefLabel "%s" ;
                       obo:GENO_0000894 ?start ;
                       obo:GENO_0000895 ?end ;
                       obo:BFO_0000050 ?chr ;
                       obo:RO_0002162 ?taxon;
                       skos:definition ?definition ;
                       dc:hasVersion ?assembly .
    }
    }
    """ %(crm)
    results=data_processing(query)
    if not results:
        return "No data available for the introduced crm or you may have introduced an instance that is not a crm. Check your data type with type_data function."
    return results

def getCRM_add_info(crm):#función que nos devuelve información adicional del CRM.
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint    
    # Construir la consulta SPARQL
    query="""
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX dc: <http://purl.org/dc/terms/>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX sch: <http://schema.org/>
    PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?evidence ?database (REPLACE(STR(?biological_samples), "http://purl.obolibrary.org/obo/", "") AS ?biological_samples) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
    WHERE {
    GRAPH <http://rdf.biogateway.eu/graph/crm> { 
               ?uri skos:prefLabel "%s" .
               ?crm_id rdfs:type ?uri .
            OPTIONAL { ?crm_id obo:TXPO_0003500 ?biological_samples. }
            OPTIONAL { ?crm_id sch:evidenceOrigin ?evidence. }
            OPTIONAL { ?crm_id sio:SIO_000772 ?articles. }
            OPTIONAL { ?crm_id sio:SIO_000253 ?database. }
    }
    }
    """%(crm)
    results=data_processing(query)   
    # Initialize combined_result dictionary
    combined_result = {
        'evidence': None,
        'database': None,
        'biological_samples': [],
        'articles': []
    }

    
    if not results:
            return "No data available for the introduced crm or you may have introduced an instance that is not a crm. Check your data type with type_data function."

    # Get the first result and update combined_result if keys are present
    first_result = results[0]
    combined_result['evidence'] = first_result.get('evidence')
    combined_result['database'] = first_result.get('database')

    # Process each result to append unique biological samples and articles
    for result in results:
        bio_sample = result.get('biological_samples')
        article = result.get('articles')
        if bio_sample and bio_sample not in combined_result['biological_samples']:
            combined_result['biological_samples'].append(bio_sample)
        if article and article not in combined_result['articles']:
            combined_result['articles'].append(article)

    # Join lists into semicolon-separated strings
    combined_result['biological_samples'] = '; '.join(combined_result['biological_samples'])
    combined_result['articles'] = '; '.join(combined_result['articles'])

    return combined_result

def getCRMs_by_coord(chromosome, start, end ):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    chromosome_ncbi=translate_chr(chromosome)
    # Construir la consulta SPARQL
    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX nuccore: <https://www.ncbi.nlm.nih.gov/nuccore/>
    SELECT DISTINCT ?crm_name ?start ?end 
    WHERE {{
            GRAPH <http://rdf.biogateway.eu/graph/crm> {{
                ?crm obo:GENO_0000894 ?start ;
                      skos:prefLabel ?crm_name ;
                      obo:GENO_0000895 ?end ;
                      obo:BFO_0000050 nuccore:%s .
                  # Filtrar por el cromosoma especificado
              FILTER (?start >= %s && ?end <= %s)
            }}
        }}
    """%(chromosome_ncbi, start, end)
    results=data_processing(query)
    if len(results)== 0:
        return "No data available for the introduced genomic coordinates."
    else:
        results_sorted = sorted(results, key=lambda x: x['crm_name'])

        return results_sorted

def getTAD_info(tad):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    
    # Construir la consulta SPARQL
    query="""
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX dc: <http://purl.org/dc/terms/>
    SELECT DISTINCT (REPLACE(STR(?chr), "https://www.ncbi.nlm.nih.gov/nuccore/", "") AS ?chromosome) ?start ?end (REPLACE(STR(?assembly), "https://www.ncbi.nlm.nih.gov/assembly/", "") AS ?assembly) (REPLACE(STR(?taxon), "http://purl.obolibrary.org/obo/", "") AS ?taxon) ?definition
     WHERE {
     GRAPH <http://rdf.biogateway.eu/graph/tad> { 
               ?tad_id skos:prefLabel "%s" ;
                       obo:GENO_0000894 ?start ;
                       obo:GENO_0000895 ?end ;
                       obo:BFO_0000050 ?chr ;
                       obo:RO_0002162 ?taxon;
                       skos:definition ?definition;
                       dc:hasVersion ?assembly .
    }
    }
    """ %(tad)
    results=data_processing(query)
    if not results:
            return "No data available for the introduced tad or you may have introduced an instance that is not a tad. Check your data type with type_data function."
    return results

def getTAD_add_info(tad):#función que nos devuelve información adicional del CRM.
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    
    # Construir la consulta SPARQL
    query="""
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX dc: <http://purl.org/dc/terms/>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX sch: <http://schema.org/>
    PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?evidence ?database 
                    (REPLACE(STR(?biological_samples), "http://purl.obolibrary.org/obo/", "") AS ?biological_samples) 
                    (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/tad> { 
            ?uri skos:prefLabel "%s" .
            ?tad_id rdfs:type ?uri .
            OPTIONAL { ?tad_id obo:TXPO_0003500 ?biological_samples. }
            OPTIONAL { ?tad_id sch:evidenceOrigin ?evidence. }
            OPTIONAL { ?tad_id sio:SIO_000772 ?articles. }
            OPTIONAL { ?tad_id sio:SIO_000253 ?database. }
        }
    }
  
    """%(tad)
    results = data_processing(query)

    # Initialize combined_result dictionary
    combined_result = {
        'evidence': None,
        'database': None,
        'biological_samples': [],
        'articles': []
    }

    # If results are empty, return the combined_result as is
    if not results:
        return "No data available for the introduced tad or you may have introduced an instance that is not a tad. Check your data type with type_data function."

    # Get the first result and update combined_result if keys are present
    first_result = results[0]
    combined_result['evidence'] = first_result.get('evidence')
    combined_result['database'] = first_result.get('database')

    # Process each result to append unique biological samples and articles
    for result in results:
        bio_sample = result.get('biological_samples')
        article = result.get('articles')
        if bio_sample and bio_sample not in combined_result['biological_samples']:
            combined_result['biological_samples'].append(bio_sample)
        if article and article not in combined_result['articles']:
            combined_result['articles'].append(article)

    # Join lists into semicolon-separated strings
    combined_result['biological_samples'] = '; '.join(combined_result['biological_samples'])
    combined_result['articles'] = '; '.join(combined_result['articles'])

    return combined_result

def getTADs_by_coord(chromosome, start, end):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    
    chromosome_ncbi=translate_chr(chromosome)
    
    # Construir la consulta SPARQL
    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX nuccore: <https://www.ncbi.nlm.nih.gov/nuccore/>
    SELECT DISTINCT ?tad_id ?start ?end 
    WHERE {{
            GRAPH <http://rdf.biogateway.eu/graph/tad> {{
                ?tad obo:GENO_0000894 ?start ;
                      skos:prefLabel ?tad_id ;
                      obo:GENO_0000895 ?end ;
                      obo:BFO_0000050 nuccore:%s ;
                      obo:RO_0002162 ?taxon .
                  # Filtrar por el cromosoma especificado
              FILTER (?start >= %s && ?end <= %s)
            }}
        }}
    """%(chromosome_ncbi, start, end)
    results=data_processing(query)
    if len(results)== 0:
        return "No data available for the introduced genomic coordinates."
    else:
        results_sorted = sorted(results, key=lambda x: x['tad_id'])

        return results_sorted

def gene2protein(gene,taxon):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    if taxon==None:
        query="""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX sio: <http://semanticscience.org/resource/>
         SELECT DISTINCT ?prot_name  
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/gene> {
                         ?gene skos:prefLabel "%s";
                               sio:SIO_010078 ?prot .
            }

            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:prefLabel ?prot_name .
            }
            }
        """%(gene)
        results=data_processing(query)
        results_sorted = sorted(results, key=lambda x: x['prot_name'])
        if not results:
            return "No data available for the introduced gene. Check that the gene id is correct or if you have introduced the taxon correctly."
        return results_sorted
    else:
        if taxon.isdigit():
            # Si se proporciona el número de taxón
            query = """
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX gene: <http://rdf.biogateway.eu/gene/%s/>
            PREFIX sio: <http://semanticscience.org/resource/>
             SELECT DISTINCT ?prot_name  
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/gene> {
                    gene:%s sio:SIO_010078 ?prot .
                }

                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot skos:prefLabel ?prot_name .
                }
                }
            """ %(taxon,gene)
            results=data_processing(query)
            results_sorted = sorted(results, key=lambda x: x['prot_name'])
            if not results:
                return "No data available for the introduced gene. Check that the gene id is correct or if you have introduced the taxon correctly."
            return results_sorted
        else:
            # Si se proporciona el nombre del taxón
            query_tax = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?taxon WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/taxon> {
                    ?taxon rdfs:label "%s"
                }
            }
            """ %(taxon)
            tax_result=data_processing(query_tax)
            tax_uri = tax_result[0]['taxon']  # Obtener la URI del taxón desde el resultado de la consulta
            # Dividir la URI utilizando el carácter '_'
            parts = tax_uri.split('_')
            # El número de taxón es el último elemento después de dividir la URI
            num_taxon = parts[-1]
            query = """
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX gene: <http://rdf.biogateway.eu/gene/%s/>
            PREFIX sio: <http://semanticscience.org/resource/>
            SELECT DISTINCT ?prot_name  
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/gene> {
                    gene:%s sio:SIO_010078 ?prot .
                }

                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot skos:prefLabel ?prot_name .
                }
                }
            """ %(num_taxon,gene)
            results=data_processing(query)
            results_sorted = sorted(results, key=lambda x: x['prot_name'])
            if not results:
                return "No data available for the introduced gene. Check that the gene id is correct or if you have introduced the taxon correctly."
            return results_sorted
        
def protein2gene(protein):
     # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    
    # Construir la consulta SPARQL
    query="""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX sio: <http://semanticscience.org/resource/>
    SELECT DISTINCT  ?gene_id
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/prot> {
            ?prot skos:prefLabel "%s" .
    }
    GRAPH <http://rdf.biogateway.eu/graph/gene> {
            ?gen sio:SIO_010078 ?prot ;
                 skos:prefLabel ?gene_id.  
        }
    }
    """ %(protein)
    results=data_processing(query)
        
    if len(results) == 0:
        query_alt_label = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX sio: <http://semanticscience.org/resource/>
        SELECT DISTINCT ?gene_id
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:altLabel "%s" .
            }
               GRAPH <http://rdf.biogateway.eu/graph/gene> {
                    ?gen sio:SIO_010078 ?prot ;
                         skos:prefLabel ?gene_id.  
        }
    }
        """%(protein)
        results=data_processing(query_alt_label)
    if len(results)== 0 :
         return "No data available for the introduced protein or you may have introduced an instance that is not a protein. Check your data type with type_data function."
    else:
        results_sorted = sorted(results, key=lambda x: x['gene_id'])
        return results_sorted

def gene2phen(gene):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    # Construir la consulta SPARQL
    query="""
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX hgene: <http://rdf.biogateway.eu/gene/9606/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT (REPLACE(STR(?omim_id), "http://purl.bioontology.org/ontology/OMIM/", "") AS ?omim_id) ?phen_label
    WHERE {
    GRAPH  <http://rdf.biogateway.eu/graph/gene2phen> {
            hgene:%s obo:RO_0002331 ?omim_id .
            ?omim_id skos:prefLabel ?phen_label . 
    }
    }
    """%(gene)
    results=data_processing(query)
    if len(results)== 0:
        return "No data available for the introduced gene or you may have introduced an instance is not a gene. Check your data type with type_data function."
    else:
        results_sorted = sorted(results, key=lambda x: x['phen_label'])
        return(results_sorted)
    
def phen2gene(phenotype):
    endpoint_sparql = sparql_endpoint
    
    # Construct the SPARQL query for general phenotype search
    query = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    SELECT DISTINCT ?gene_name
    WHERE {{
        GRAPH <http://rdf.biogateway.eu/graph/omim> {{
            {{?omim_id skos:prefLabel ?label}}
            UNION
            {{?omim_id skos:altLabel ?label}}
        }}
        FILTER regex(?label, "{phenotype}", "i")
        GRAPH <http://rdf.biogateway.eu/graph/gene2phen> {{
            ?gene obo:RO_0002331 ?omim_id .
        }}
        GRAPH <http://rdf.biogateway.eu/graph/gene> {{
            ?gene sio:SIO_010078 ?prot ;
                  skos:prefLabel ?gene_name.
        }}
    }}
    """
    
    results = data_processing(query)
    
    if len(results) == 0:
        # Check if the phenotype is a valid OMIM identifier
        if phenotype.isdigit() and len(phenotype) == 6 or phenotype.startswith("MTHU"):
            query_phen = f"""
            PREFIX omim: <http://purl.bioontology.org/ontology/OMIM/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            SELECT DISTINCT ?gene_name
            WHERE {{
                GRAPH  <http://rdf.biogateway.eu/graph/gene2phen> {{
                    ?gene obo:RO_0002331 omim:{phenotype} .
               }}
                GRAPH <http://rdf.biogateway.eu/graph/gene> {{
                    ?gene skos:prefLabel ?gene_name.  
                }}
            }}
            """ 
            results = data_processing(query_phen)
    if len(results) != 0:
        results_sorted = sorted(results, key=lambda x: x['gene_name'])
        return results_sorted
    else:
        return "No data available for the introduced phenotype or you may have introduced an instance that is not a phenotype. Check your data type with type_data function."



def prot2bp(protein):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    query="""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT  ?bp_id ?bp_label   ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) 
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/prot> {
            ?prot skos:prefLabel "%s" .
        }
        GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
            ?prot obo:RO_0002331 ?bp .
        GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
            ?uri rdf:subject ?prot ;
                 rdf:predicate ?relation ;
                 rdf:object ?bp ;
                 skos:prefLabel ?relation_label .
        }
        }
        GRAPH <http://rdf.biogateway.eu/graph/go> {
            ?bp rdfs:label ?bp_label ;
                oboowl:id ?bp_id .
        }
        BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
        GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                ?uri_with_goa sio:SIO_000772 ?articles ;
                              sio:SIO_000253 ?database .
        }
    }
    """ %(protein)
    results=data_processing(query)
        
    if len(results) == 0:
        query_alt_label = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?bp_id ?bp_label  ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:altLabel "%s" .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                    ?prot obo:RO_0002331 ?bp .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?bp ;
                         skos:prefLabel ?relation_label .
                }
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                    ?bp rdfs:label ?bp_label ;
                        oboowl:id ?bp_id .

                }
                BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                  GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                        ?uri_with_goa sio:SIO_000772 ?articles ;
                                      sio:SIO_000253 ?database .
        }
        }
        """%(protein)
        results=data_processing(query_alt_label)
    if not results:
         return "No data available for the introduced protein or you may have introduced an instance that is not a protein. Check your data type with type_data function."
    
    combined_results = defaultdict(lambda: {"bp_id": "", "bp_label": "", "relation_label": "", "database": "", "articles": set()})

    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['bp_id'], entry['bp_label'], entry['relation_label'], entry['database'])
        combined_results[key]['bp_id'] = entry['bp_id']
        combined_results[key]['bp_label'] = entry['bp_label']
        combined_results[key]['relation_label'] = entry['relation_label']
        combined_results[key]['database'] = entry['database']
        combined_results[key]['articles'].add(entry['articles'])

    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(entry['articles'])
        final_results.append(entry)
    results_sorted = sorted(final_results, key=lambda x: x['bp_label'])
    return results_sorted

def bp2prot(biological_process, taxon):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    if taxon is None: # Si no ponemos taxon
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
        PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
        SELECT DISTINCT ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/go> {
                  ?bp rdfs:label ?bp_label.
            }
            FILTER regex(?bp_label, '%s', "i")
            GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                ?prot obo:RO_0002331 ?bp.
            }
            GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                ?uri rdf:subject ?prot;
                     rdf:predicate ?relation;
                     rdf:object ?bp;
                     skos:prefLabel ?relation_label.
            }
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?prot skos:prefLabel ?protein_name.
            }
            BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
            GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                ?uri_with_goa sio:SIO_000772 ?articles;
                              sio:SIO_000253 ?database.
            }
        }
        ORDER BY ?protein_name ?articles
        """ % (biological_process)
        results = data_processing(query)
        if len(results) == 0:
            query_alt = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            PREFIX sio: <http://semanticscience.org/resource/>
            PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
            PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
            SELECT DISTINCT ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                      ?bp oboowl:id "%s".
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                    ?prot obo:RO_0002331 ?bp.
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                    ?uri rdf:subject ?prot;
                         rdf:predicate ?relation;
                         rdf:object ?bp;
                         skos:prefLabel ?relation_label.
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:prefLabel ?protein_name.
                }
                BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                    ?uri_with_goa sio:SIO_000772 ?articles;
                                  sio:SIO_000253 ?database.
                }
            }
            ORDER BY ?protein_name ?articles
            """ % (biological_process)
            results = data_processing(query_alt)
    else:
        if taxon.isdigit():
            query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            PREFIX sio: <http://semanticscience.org/resource/>
            PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
            PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
            SELECT DISTINCT ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                      ?bp rdfs:label ?bp_label.
                }
                FILTER regex(?bp_label, '%s', "i")
                GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                    ?prot obo:RO_0002331 ?bp.
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                    ?uri rdf:subject ?prot;
                         rdf:predicate ?relation;
                         rdf:object ?bp;
                         skos:prefLabel ?relation_label.
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot obo:RO_0002162 tax:%s;
                          skos:prefLabel ?protein_name.
                }
                BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                    ?uri_with_goa sio:SIO_000772 ?articles;
                                  sio:SIO_000253 ?database.
                }
            }
            ORDER BY ?protein_name ?articles
            """ % (biological_process, taxon)
            results = data_processing(query)
            if len(results) == 0:
                query_alt = """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX obo: <http://purl.obolibrary.org/obo/>
                PREFIX sio: <http://semanticscience.org/resource/>
                PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
                PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
                SELECT DISTINCT ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
                WHERE {
                    GRAPH <http://rdf.biogateway.eu/graph/go> {
                          ?bp oboowl:id "%s".
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                        ?prot obo:RO_0002331 ?bp.
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                        ?uri rdf:subject ?prot;
                             rdf:predicate ?relation;
                             rdf:object ?bp;
                             skos:prefLabel ?relation_label.
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot obo:RO_0002162 tax:%s;
                              skos:prefLabel ?protein_name.
                    }
                    BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                    GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                        ?uri_with_goa sio:SIO_000772 ?articles;
                                      sio:SIO_000253 ?database.
                    }
                }
                ORDER BY ?protein_name ?articles
                """ % (biological_process, taxon)
                results = data_processing(query_alt)
        else:
            query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            PREFIX sio: <http://semanticscience.org/resource/>
            PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
            SELECT DISTINCT ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                      ?bp rdfs:label ?bp_label.
                }
                FILTER regex(?bp_label, '%s', "i")
                GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                    ?prot obo:RO_0002331 ?bp.
                }
                GRAPH <http://rdf.biogateway.eu/graph/taxon> {
                    ?taxon rdfs:label "%s".
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                    ?uri rdf:subject ?prot;
                         rdf:predicate ?relation;
                         rdf:object ?bp;
                         skos:prefLabel ?relation_label.
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot obo:RO_0002162 ?taxon;
                          skos:prefLabel ?protein_name.
                }
                BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                    ?uri_with_goa sio:SIO_000772 ?articles;
                                  sio:SIO_000253 ?database.
                }
            }
            ORDER BY ?protein_name ?articles
            """ % (biological_process, taxon)
            results = data_processing(query)
            if len(results) == 0:
                query_alt = """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX obo: <http://purl.obolibrary.org/obo/>
                PREFIX sio: <http://semanticscience.org/resource/>
                PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
                PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
                SELECT DISTINCT ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
                WHERE {
                    GRAPH <http://rdf.biogateway.eu/graph/go> {
                          ?bp oboowl:id "%s".
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                        ?prot obo:RO_0002331 ?bp.
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/taxon> {
                        ?taxon rdfs:label "%s".
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                        ?uri rdf:subject ?prot;
                             rdf:predicate ?relation;
                             rdf:object ?bp;
                             skos:prefLabel ?relation_label.
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot obo:RO_0002162 ?taxon;
                              skos:prefLabel ?protein_name.
                    }
                    BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                    GRAPH <http://rdf.biogateway.eu/graph/prot2bp> {
                        ?uri_with_goa sio:SIO_000772 ?articles;
                                      sio:SIO_000253 ?database.
                    }
                }
                ORDER BY ?protein_name ?articles
                """ % (biological_process, taxon)
                results = data_processing(query_alt)
    
    combined_results = defaultdict(lambda: {"protein_name": "", "relation_label": "", "database": "", "articles": set()})
    if not results:
        return "No data available for the introduced biological process. Check that the biological process id is correct or if you have introduced the taxon correctly."
    
    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['protein_name'], entry['relation_label'], entry['database'])
        combined_results[key]['protein_name'] = entry['protein_name']
        combined_results[key]['relation_label'] = entry['relation_label']
        combined_results[key]['database'] = entry['database']
        combined_results[key]['articles'].add(entry['articles'])

    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles']))  # Ordenar artículos antes de unirlos
        final_results.append(entry)
    
    # Ordenar los resultados finales
    final_results = sorted(final_results, key=lambda x: (x['protein_name'], x['relation_label'], x['database']))
    
    return final_results

def prot2cc(protein):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    query="""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT  ?cc_id ?cc_label  ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)  
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/prot> {
            ?prot skos:prefLabel "%s" .
        }
        GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
            ?prot obo:BFO_0000050 ?cc .
        }
        GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                ?uri rdf:subject ?prot ;
                        rdf:predicate ?relation ;
                        rdf:object ?cc ;
                        skos:prefLabel ?relation_label .
            }
        GRAPH <http://rdf.biogateway.eu/graph/go> {
            ?cc rdfs:label ?cc_label ;
                oboowl:id ?cc_id .
        }
        BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
        GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
            ?uri_with_goa sio:SIO_000772 ?articles ;
                          sio:SIO_000253 ?database .
    }
    }
    """ %(protein)
    results=data_processing(query)
        
    if len(results) == 0:
        query_alt_label = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?cc_id ?cc_label  ?relation_label  (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) 
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:altLabel "%s" .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?prot obo:BFO_0000050 ?cc .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?cc ;
                         skos:prefLabel ?relation_label .
                }
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                    ?cc rdfs:label ?cc_label ;
                        oboowl:id ?cc_id .
                }
                  BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                  GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?uri_with_goa sio:SIO_000772 ?articles ;
                                  sio:SIO_000253 ?database .
        }
        }
        """%(protein)
        results=data_processing(query_alt_label)
    combined_results = defaultdict(lambda: {"cc_id": "", "cc_label": "", "relation_label": "", "database": "", "articles": set()})
    if not results:
         return "No data available for the introduced protein or you may have introduced an instance that is not a protein. Check your data type with type_data function."
    
    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['cc_id'], entry['cc_label'], entry['relation_label'], entry['database'])
        combined_results[key]['cc_id'] = entry['cc_id']
        combined_results[key]['cc_label'] = entry['cc_label']
        combined_results[key]['relation_label'] = entry['relation_label']
        combined_results[key]['database'] = entry['database']
        combined_results[key]['articles'].add(entry['articles'])

    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(entry['articles'])
        final_results.append(entry)
    results_sorted = sorted(final_results, key=lambda x: x['cc_label'])
    return results_sorted

def cc2prot(cellular_component,taxon):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    if taxon== None:
        query="""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
        PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT  ?protein_name ?relation_label  (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) 
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/go> {
                  ?cc rdfs:label ?cc_label.
            }
             FILTER regex(?cc_label, "%s", "i")
            GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                ?prot obo:BFO_0000050 ?cc .
            }
            GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?cc ;
                         skos:prefLabel ?relation_label .
            }
             GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?prot skos:prefLabel ?protein_name .
            }
            BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
            GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?uri_with_goa sio:SIO_000772 ?articles ;
                                  sio:SIO_000253 ?database .
            }
            }
            ORDER BY ?protein_name ?articles
            """ %(cellular_component)
        results=data_processing(query)
        if len(results)==0:
            query_alt="""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            PREFIX sio: <http://semanticscience.org/resource/>
            PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
            PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT DISTINCT  ?protein_name ?relation_label  (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) 
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                      ?cc oboowl:id "%s" .
                }
                 GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                ?prot obo:BFO_0000050 ?cc .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?cc ;
                         skos:prefLabel ?relation_label .
                }
                 GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:prefLabel ?protein_name .
                }
                BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                  GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?uri_with_goa sio:SIO_000772 ?articles ;
                                  sio:SIO_000253 ?database .
                }
                }
                ORDER BY ?protein_name ?articles
                """ %(cellular_component)
            results=data_processing(query_alt)
    else:
        if taxon.isdigit():
            query="""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            PREFIX sio: <http://semanticscience.org/resource/>
            PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
            PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT DISTINCT  ?protein_name ?relation_label  (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) 
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                      ?cc rdfs:label ?cc_label.
                }
                 FILTER regex(?cc_label, "%s", "i")
                GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?prot obo:BFO_0000050 ?cc .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?cc ;
                         skos:prefLabel ?relation_label .
                }
                 GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot obo:RO_0002162 tax:%s ;
                          skos:prefLabel ?protein_name .
                }
                BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                  GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?uri_with_goa sio:SIO_000772 ?articles ;
                                  sio:SIO_000253 ?database .
                }
                }
                ORDER BY ?protein_name ?articles
                """%(cellular_component, taxon)
            results=data_processing(query)
            if len(results)==0:
                query_alt="""
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX obo: <http://purl.obolibrary.org/obo/>
                PREFIX sio: <http://semanticscience.org/resource/>
                PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
                PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT DISTINCT  ?protein_name ?relation_label  (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
                WHERE {
                    GRAPH <http://rdf.biogateway.eu/graph/go> {
                          ?cc oboowl:id "%s" .
                    }
                     GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                        ?prot obo:BFO_0000050 ?cc .
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                        ?uri rdf:subject ?prot ;
                             rdf:predicate ?relation ;
                             rdf:object ?cc ;
                             skos:prefLabel ?relation_label .
                    }
                     GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot obo:RO_0002162 tax:%s ;
                              skos:prefLabel ?protein_name .
                    }
                    BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                      GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                        ?uri_with_goa sio:SIO_000772 ?articles ;
                                      sio:SIO_000253 ?database .
                    }
                    }
                    ORDER BY ?protein_name ?articles
                    """%(cellular_component, taxon)
                results=data_processing(query_alt)
        else:
            # Construir la consulta SPARQL
            query="""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            PREFIX sio: <http://semanticscience.org/resource/>
            PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT DISTINCT  ?protein_name ?relation_label  (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                      ?cc rdfs:label ?cc_label.
                }
                 FILTER regex(?cc_label, "%s", "i")
                GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?prot obo:BFO_0000050 ?cc .
                }
                GRAPH <http://rdf.biogateway.eu/graph/taxon> {
                        ?taxon rdfs:label "%s" .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?cc ;
                         skos:prefLabel ?relation_label .
                }

                 GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot obo:RO_0002162 ?taxon ;
                          skos:prefLabel ?protein_name .
                }
                BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                  GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                    ?uri_with_goa sio:SIO_000772 ?articles ;
                                  sio:SIO_000253 ?database .
                }
                }
                ORDER BY ?protein_name ?articles
                """%(cellular_component, taxon)
            results=data_processing(query)
            if len(results)==0:
                query_alt="""
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX obo: <http://purl.obolibrary.org/obo/>
                PREFIX sio: <http://semanticscience.org/resource/>
                PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
                PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT DISTINCT  ?protein_name ?relation_label  (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
                WHERE {
                    GRAPH <http://rdf.biogateway.eu/graph/go> {
                          ?cc oboowl:id "%s" .
                    }
                     GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                        ?prot obo:BFO_0000050 ?cc .
                    }
                     GRAPH <http://rdf.biogateway.eu/graph/taxon> {
                        ?taxon rdfs:label "%s" .
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                        ?uri rdf:subject ?prot ;
                             rdf:predicate ?relation ;
                             rdf:object ?cc ;
                             skos:prefLabel ?relation_label .
                    }
                     GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot obo:RO_0002162 ?taxon ;
                              skos:prefLabel ?protein_name .
                    }
                    BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                      GRAPH <http://rdf.biogateway.eu/graph/prot2cc> {
                        ?uri_with_goa sio:SIO_000772 ?articles ;
                                      sio:SIO_000253 ?database .
                    }
                    }
                    ORDER BY ?protein_name ?articles
                    """%(cellular_component, taxon)
                results=data_processing(query_alt)
    combined_results = defaultdict(lambda: {"protein_name": "", "relation_label": "", "database": "", "articles": set()})
    if not results:
        return "No data available for the introduced cellular component. Check that the cellular component id is correct or if you have introduced the taxon correctly."
    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['protein_name'], entry['relation_label'], entry['database'])
        combined_results[key]['protein_name'] = entry['protein_name']
        combined_results[key]['relation_label'] = entry['relation_label']
        combined_results[key]['database'] = entry['database']
        combined_results[key]['articles'].add(entry['articles'])

    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles']))
        final_results.append(entry)
    final_results = sorted(final_results, key=lambda x: (x['protein_name'], x['relation_label'], x['database']))
    return final_results

def prot2mf(protein):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    query="""        
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?mf_id ?mf_label  ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:prefLabel "%s" .
                }
            GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                    ?prot obo:RO_0002327 ?mf .
                    
            }
                GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?mf ;
                         skos:prefLabel ?relation_label .
            }
            GRAPH <http://rdf.biogateway.eu/graph/go> {
                    ?mf rdfs:label ?mf_label ;
                        oboowl:id ?mf_id .

            }
    BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
    GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
        ?uri_with_goa sio:SIO_000772 ?articles ;
                      sio:SIO_000253 ?database .
    }
        }

    """ %(protein)
    results=data_processing(query)
        
    if len(results) == 0:
        query_alt_label = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?mf_id ?mf_label ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:altLabel "%s" .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                    ?prot obo:RO_0002327 ?mf .
                    
                }
                 GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?mf ;
                         skos:prefLabel ?relation_label .
                }
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                    ?mf rdfs:label ?mf_label ;
                        oboowl:id ?mf_id .
                }    
                BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?uri_with_goa sio:SIO_000772 ?articles ;
                                      sio:SIO_000253 ?database .
        }
        }
        """%(protein)
        results=data_processing(query_alt_label)

    combined_results = defaultdict(lambda: {"mf_id": "", "mf_label": "", "relation_label": "", "database": "", "articles": set()})
    if not results:
         return "No data available for the introduced protein or you may have introduced an instance that is not a protein. Check your data type with type_data function."
    
    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['mf_id'], entry['mf_label'], entry['relation_label'], entry['database'])
        combined_results[key]['mf_id'] = entry['mf_id']
        combined_results[key]['mf_label'] = entry['mf_label']
        combined_results[key]['relation_label'] = entry['relation_label']
        combined_results[key]['database'] = entry['database']
        combined_results[key]['articles'].add(entry['articles'])

    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(entry['articles'])
        final_results.append(entry)
    results_sorted = sorted(final_results, key=lambda x: x['mf_label'])
    return results_sorted

def mf2prot(molecular_function,taxon):
    # Endpoint SPARQL
    endpoint_sparql = sparql_endpoint
    if taxon== None:
        query="""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
        PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT  ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/go> {
                  ?mf rdfs:label ?mf_label.
            }
             FILTER regex(?mf_label, "%s", "i")
            GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                ?prot obo:RO_0002327 ?mf .
            }
             GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?prot skos:prefLabel ?protein_name .
            }
            GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?mf ;
                         skos:prefLabel ?relation_label .
                }
            BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
            GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?uri_with_goa sio:SIO_000772 ?articles ;
                                      sio:SIO_000253 ?database .
            }
            }
            ORDER BY ?protein_name ?articles
            """ %(molecular_function)
        results=data_processing(query)
        if len(results)==0: #si molecular function es identificador se ejecuta esto
            query_alt="""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            PREFIX sio: <http://semanticscience.org/resource/>
            PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
            PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT DISTINCT  ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                      ?mf oboowl:id "%s" .
                }
                 GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                ?prot obo:RO_0002327 ?mf .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?mf ;
                         skos:prefLabel ?relation_label .
                }
                 GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:prefLabel ?protein_name .
                }
                BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?uri_with_goa sio:SIO_000772 ?articles ;
                                      sio:SIO_000253 ?database .
                }
                }
                ORDER BY ?protein_name ?articles
                """%(molecular_function)
            results=data_processing(query_alt)
        return results
    else:
        if taxon.isdigit(): #si el taxon es numero se ejecuta esta consulta primero, que es cuando molecular function es una palabra
            query="""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            PREFIX sio: <http://semanticscience.org/resource/>
            PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
            PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT DISTINCT  ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                      ?mf rdfs:label ?mf_label.
                }
                 FILTER regex(?mf_label, "%s", "i")
                GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                    ?prot obo:RO_0002327 ?mf .
                }
                 GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot obo:RO_0002162 tax:%s ;
                          skos:prefLabel ?protein_name .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?uri rdf:subject ?prot ;
                             rdf:predicate ?relation ;
                             rdf:object ?mf ;
                             skos:prefLabel ?relation_label .
                    }
                BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?uri_with_goa sio:SIO_000772 ?articles ;
                                      sio:SIO_000253 ?database .
                }
                }
                ORDER BY ?protein_name ?articles
                """ %(molecular_function, taxon)
            results=data_processing(query)
            if len(results)==0: #si molecular function es identificador se ejecuta esto
                query_alt="""
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX obo: <http://purl.obolibrary.org/obo/>
                PREFIX sio: <http://semanticscience.org/resource/>
                PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
                PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT DISTINCT  ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
                WHERE {
                    GRAPH <http://rdf.biogateway.eu/graph/go> {
                          ?mf oboowl:id "%s" .
                    }
                     GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                    ?prot obo:RO_0002327 ?mf .
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?uri rdf:subject ?prot ;
                             rdf:predicate ?relation ;
                             rdf:object ?mf ;
                             skos:prefLabel ?relation_label .
                    }
                     GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot obo:RO_0002162 tax:%s ;
                              skos:prefLabel ?protein_name .
                    }
                    BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                    GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?uri_with_goa sio:SIO_000772 ?articles ;
                                      sio:SIO_000253 ?database .
                    }
                    }
                    ORDER BY ?protein_name ?articles
                    """%(molecular_function, taxon)
                results=data_processing(query_alt)
        else:
            # Construir la consulta SPARQL
            query="""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            PREFIX sio: <http://semanticscience.org/resource/>
            PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT DISTINCT  ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/go> {
                      ?mf rdfs:label ?mf_label.
                }
                 FILTER regex(?mf_label, "%s", "i")
                GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                    ?prot obo:RO_0002327 ?mf .
                }
                GRAPH <http://rdf.biogateway.eu/graph/taxon> {
                        ?taxon rdfs:label "%s" .
                }

                 GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot obo:RO_0002162 ?taxon ;
                          skos:prefLabel ?protein_name .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?uri rdf:subject ?prot ;
                             rdf:predicate ?relation ;
                             rdf:object ?mf ;
                             skos:prefLabel ?relation_label .
                    }
                BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?uri_with_goa sio:SIO_000772 ?articles ;
                                      sio:SIO_000253 ?database .
                }
                }
                ORDER BY ?protein_name ?articles
                """%(molecular_function, taxon)
            results=data_processing(query)
            if len(results)==0:
                query_alt="""
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX obo: <http://purl.obolibrary.org/obo/>
                PREFIX sio: <http://semanticscience.org/resource/>
                PREFIX tax: <http://purl.obolibrary.org/obo/NCBITaxon_>
                PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT DISTINCT  ?protein_name ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) 
                WHERE {
                    GRAPH <http://rdf.biogateway.eu/graph/go> {
                          ?mf oboowl:id "%s" .
                    }
                     GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?prot obo:RO_0002327 ?mf .
                    }
                     GRAPH <http://rdf.biogateway.eu/graph/taxon> {
                        ?taxon rdfs:label "%s" .
                    }

                     GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot obo:RO_0002162 ?taxon ;
                              skos:prefLabel ?protein_name .
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?uri rdf:subject ?prot ;
                             rdf:predicate ?relation ;
                             rdf:object ?mf ;
                             skos:prefLabel ?relation_label .
                    }
                    BIND(IRI(CONCAT(STR(?uri), "#goa")) AS ?uri_with_goa)
                    GRAPH <http://rdf.biogateway.eu/graph/prot2mf> {
                        ?uri_with_goa sio:SIO_000772 ?articles ;
                                      sio:SIO_000253 ?database .
                    }
                    }
                    ORDER BY ?protein_name ?articles
                    """%(molecular_function, taxon)
                results=data_processing(query_alt)
    combined_results = defaultdict(lambda: {"protein_name": "", "relation_label": "", "database": "", "articles": set()})
    if not results:
        return "No data available for the introduced molecular function. Check that the molecular function id is correct or if you have introduced the taxon correctly."
    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['protein_name'], entry['relation_label'], entry['database'])
        combined_results[key]['protein_name'] = entry['protein_name']
        combined_results[key]['relation_label'] = entry['relation_label']
        combined_results[key]['database'] = entry['database']
        combined_results[key]['articles'].add(entry['articles'])

    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles']))
        final_results.append(entry)
    final_results = sorted(final_results, key=lambda x: (x['protein_name'], x['relation_label'], x['database']))
    return final_results

def gene2crm(gene):
    endpoint_sparql = sparql_endpoint
    query="""
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX sio: <http://semanticscience.org/resource/>
    SELECT DISTINCT ?crm_name ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/gene> {
            ?gene skos:prefLabel "%s". 
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm2gene> {
            ?crm obo:RO_0002429 ?gene.
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm> {
            ?crm skos:prefLabel ?crm_name .
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm2gene> {
            ?uri rdfs:object ?gene .
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm2gene> {
            ?s rdfs:type ?uri ;
               sio:SIO_000772 ?articles ;
               sio:SIO_000253 ?database .
        }
    }
    """ %(gene)
    results=data_processing(query)
    combined_results = defaultdict(lambda: {"crm_name": "", "database": set(), "articles": set()})
    if not results:
        return "No data available for the introduced gene or you may have introduced an instance that is not a gene. Check your data type with type_data function." 
    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['crm_name'])
        combined_results[key]['crm_name'] = entry['crm_name']
        combined_results[key]['database'].add(entry['database'])
        combined_results[key]['articles'].add(entry['articles'])

    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles']))  # Ordenar artículos
        entry['database'] = '; '.join(sorted(entry['database']))  # Ordenar bases de datos
        final_results.append(entry)
    # Ordenar los resultados finales por nombre de CRM
    final_results = sorted(final_results, key=lambda x: x['crm_name'])
    return final_results

def crm2gene(crm):
    endpoint_sparql = sparql_endpoint
    query="""
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX sio: <http://semanticscience.org/resource/>
    SELECT DISTINCT ?gene_name ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
    WHERE {
         GRAPH <http://rdf.biogateway.eu/graph/crm> {
                ?crm skos:prefLabel "%s" .
        }
        
        GRAPH <http://rdf.biogateway.eu/graph/crm2gene> {
            ?crm obo:RO_0002429 ?gene.
        }
        GRAPH <http://rdf.biogateway.eu/graph/gene> {
            ?gene skos:prefLabel ?gene_name. 
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm2gene> {
            ?uri rdfs:subject ?crm .
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm2gene> {
            ?s rdfs:type ?uri ;
               sio:SIO_000772 ?articles ;
               sio:SIO_000253 ?database .
        }
    }
    ORDER BY ?gene_name
    """ %(crm)
    results=data_processing(query)
    combined_results = defaultdict(lambda: {"gene_name": "", "database": set(), "articles": set()})

    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['gene_name'])
        combined_results[key]['gene_name'] = entry['gene_name']
        combined_results[key]['database'].add(entry['database'])
        combined_results[key]['articles'].add(entry['articles'])

    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles']))
        entry['database'] = '; '.join(sorted(entry['database']))
        final_results.append(entry)
    if not results:
        return "No data available for the introduced crm or you may have introduced an instance that is not a crm. Check your data type with type_data function."     
    results_sorted = sorted(final_results, key=lambda x: x['gene_name'])
    return results_sorted


def tfac2crm(tfac):
    endpoint_sparql = sparql_endpoint
    query="""
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX sch: <http://schema.org/>

    SELECT DISTINCT ?crm_name ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) (REPLACE(STR(?biological_samples), "http://purl.obolibrary.org/obo/", "") AS ?biological_samples) ?evidence
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/prot> {
            ?tfac skos:prefLabel "%s" .
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm2tfac> {
            ?crm obo:RO_0002436 ?tfac .
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm> {
            ?crm skos:prefLabel ?crm_name .
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm2tfac> {
            ?s rdfs:subject ?crm ; 
               rdfs:predicate ?relation ; 
               rdfs:object ?tfac .
           ?uri rdfs:type ?s .
            OPTIONAL { ?uri  sio:SIO_000772 ?articles . }
            OPTIONAL { ?uri sio:SIO_000253 ?database . }
            OPTIONAL { ?uri  obo:TXPO_0003500 ?biological_samples . }
            OPTIONAL { ?uri   sch:evidenceOrigin ?evidence . }
        }
    }
    """ %(tfac)
    results=data_processing(query)
    combined_results = defaultdict(lambda: {"crm_name": "", "database": set(), "articles": set(), "evidence": "", "biological_samples": set()} )
    if not results:
        return "No data available for the introduced transcription factor or you may have introduced an instance that is not a transcirption factor. Check your data type with type_data function" 
    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['crm_name'],entry['evidence'])
        combined_results[key]['crm_name'] = entry['crm_name']
        combined_results[key]['evidence'] = entry['evidence']
        combined_results[key]['database'].add(entry['database'])
        combined_results[key]['articles'].add(entry['articles'])
        combined_results[key]['biological_samples'].add(entry['biological_samples'])
    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles']))
        entry['database'] = '; '.join(sorted(entry['database']))
        entry['biological_samples'] = '; '.join(sorted(entry['biological_samples']))
        final_results.append(entry)
    
    results_sorted = sorted(final_results, key=lambda x: x['crm_name'])
    return results_sorted


def crm2tfac(crm):
    endpoint_sparql = sparql_endpoint
    query="""
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX sch: <http://schema.org/>

    SELECT DISTINCT ?tfac_name ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) (REPLACE(STR(?biological_samples), "http://purl.obolibrary.org/obo/", "") AS ?biological_samples) ?evidence
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/crm> {
            ?crm skos:prefLabel "%s" .
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm2tfac> {
            ?crm obo:RO_0002436 ?tfac .
        }
        GRAPH <http://rdf.biogateway.eu/graph/prot> {
            ?tfac skos:prefLabel ?tfac_name .
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm2tfac> {
            ?s rdfs:subject ?crm ; 
               rdfs:predicate ?relation ; 
               rdfs:object ?tfac .
            ?uri rdfs:type ?s .
            OPTIONAL { ?uri  sio:SIO_000772 ?articles . }
            OPTIONAL { ?uri sio:SIO_000253 ?database . }
            OPTIONAL { ?uri  obo:TXPO_0003500 ?biological_samples . }
            OPTIONAL { ?uri   sch:evidenceOrigin ?evidence . }
        }
    }
    """ %(crm)
    results=data_processing(query)
    combined_results = defaultdict(lambda: {"tfac_name": "", "database": set(), "articles": set(), "evidence": "", "biological_samples": set()} )
    if not results:
        return "No data available for the introduced crm or you may have introduced an instance that is not a crm. Check your data type with type_data function."    
    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['tfac_name'],entry['evidence'])
        combined_results[key]['tfac_name'] = entry['tfac_name']
        combined_results[key]['evidence'] = entry['evidence']
        combined_results[key]['database'].add(entry['database'])
        combined_results[key]['articles'].add(entry['articles'])
        combined_results[key]['biological_samples'].add(entry['biological_samples'])
    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles']))
        entry['database'] = '; '.join(sorted(entry['database']))
        entry['biological_samples'] = '; '.join(sorted(entry['biological_samples']))
        final_results.append(entry)
    else:
        results_sorted = sorted(final_results, key=lambda x: x['tfac_name'])
        return results_sorted


def crm2phen(crm):
    endpoint_sparql = sparql_endpoint
    query="""
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX sio: <http://semanticscience.org/resource/>
    SELECT DISTINCT (REPLACE(REPLACE(REPLACE(STR(?phen_id), "http://purl.bioontology.org/ontology/OMIM/", "OMIM/"), 
                 "https://id.nlm.nih.gov/mesh/", "MESH/"), 
                 "http://purl.obolibrary.org/obo/", "DOID/") AS ?phen_id)  ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) (REPLACE(STR(?biological_samples), "http://purl.obolibrary.org/obo/", "") AS ?biological_samples) ?experimental_evidence
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/crm> {
            ?crm skos:prefLabel "%s" .
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm2phen> {
            ?crm obo:RO_0002331 ?phen_id .
        }
        GRAPH <http://rdf.biogateway.eu/graph/crm2phen> {
            ?s rdfs:subject ?crm ; 
               rdfs:predicate ?relation ; 
               rdfs:object ?phen .
            ?uri rdfs:type ?s .
            OPTIONAL { ?uri  sio:SIO_000772 ?articles . }
            OPTIONAL { ?uri sio:SIO_000253 ?database . }
        }
    }
    """ %(crm)
    results=data_processing(query)
    if not results:
        return "No data available for the introduced crm or you may have introduced an instance that is not a crm. Check your data type with type_data function."    
    combined_results = defaultdict(lambda: {"phen_id": "", "database": set(), "articles": set()})

    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['phen_id'])
        combined_results[key]['phen_id'] = entry['phen_id']
        combined_results[key]['database'].add(entry['database'])
        combined_results[key]['articles'].add(entry['articles'])

    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles']))
        entry['database'] = '; '.join(sorted(entry['database']))
        final_results.append(entry)
    results_sorted = sorted(final_results, key=lambda x: x['phen_id'])
    return results_sorted


def phen2crm(phenotype):
    endpoint_sparql = sparql_endpoint
    query = f"""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        SELECT DISTINCT ?crm_name (REPLACE(STR(?omim_id), "http://purl.bioontology.org/ontology/OMIM/", "OMIM/") AS ?omim_id) ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)
        WHERE {{
            GRAPH <http://rdf.biogateway.eu/graph/omim> {{
                {{?omim_id skos:prefLabel ?label}}
                UNION
                {{?omim_id skos:altLabel ?label}}
                FILTER regex(?label, "{phenotype}", "i")
            }}
            GRAPH <http://rdf.biogateway.eu/graph/crm2phen> {{
                ?crm obo:RO_0002331 ?omim_id.
            }}
            GRAPH <http://rdf.biogateway.eu/graph/crm> {{
                ?crm skos:prefLabel ?crm_name .
            }}
            GRAPH <http://rdf.biogateway.eu/graph/crm2phen> {{
                ?s rdfs:subject ?crm ; 
                   rdfs:predicate ?relation ; 
                   rdfs:object ?phen .
                ?uri rdfs:type ?s .
                OPTIONAL {{ ?uri sio:SIO_000772 ?articles . }}
                OPTIONAL {{ ?uri sio:SIO_000253 ?database . }}
            }}
        }}
    """
    
    results = data_processing(query)

    if len(results) == 0:

        if phenotype.isdigit() and (len(phenotype) == 6 or phenotype.startswith("MTHU")):
            alt_query = f"""
            PREFIX obo: <http://purl.obolibrary.org/obo/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX sio: <http://semanticscience.org/resource/>
            PREFIX omim:<http://purl.bioontology.org/ontology/OMIM/>
            SELECT DISTINCT ?crm_name ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) 
            WHERE {{
                GRAPH <http://rdf.biogateway.eu/graph/crm2phen> {{
                    ?crm obo:RO_0002331 omim:{phenotype} .
                }}
                GRAPH <http://rdf.biogateway.eu/graph/crm> {{
                    ?crm skos:prefLabel ?crm_name .
                }}
                GRAPH <http://rdf.biogateway.eu/graph/crm2phen> {{
                    ?s rdfs:subject ?crm ; 
                       rdfs:predicate ?relation ; 
                       rdfs:object ?phen .
                    ?uri rdfs:type ?s .
                    OPTIONAL {{ ?uri sio:SIO_000772 ?articles . }}
                    OPTIONAL {{ ?uri sio:SIO_000253 ?database . }}
                }}
            }}
            """
            results = data_processing(alt_query)

    # Procesamiento de los resultados
    combined_results = defaultdict(lambda: {"crm_name": "", "omim_id": set(), "database": set(), "articles": set()})

    for entry in results:
        if 'crm_name' in entry:
            key = entry['crm_name']
            combined_results[key]['crm_name'] = entry['crm_name']
            if 'omim_id' in entry:
                combined_results[key]['omim_id'].add(entry['omim_id'])
            if 'database' in entry:
                combined_results[key]['database'].add(entry['database'])
            if 'articles' in entry:
                combined_results[key]['articles'].add(entry['articles'])

    final_results = []
    for entry in combined_results.values():
        # Asegúrate de que no eliminas entradas necesarias
        entry['omim_id'] = '; '.join(entry['omim_id']) if entry['omim_id'] else ''
        entry['database'] = '; '.join(entry['database']) if entry['database'] else ''
        entry['articles'] = '; '.join(entry['articles']) if entry['articles'] else ''
        
        # Asegúrate de añadir a final_results
        if entry['crm_name']:  # Solo añadir si hay un crm_name
            final_results.append(entry)

    if len(final_results) != 0:
        results_sorted = sorted(final_results, key=lambda x: x['crm_name'])
        return results_sorted
    else:
        return "No data available for the introduced phenotype or you may have introduced an instance that is not a phenotype. Check your data type with type_data function."

def tfac2gene(tfac, regulation_type="all"):
    endpoint_sparql = sparql_endpoint

    # Consulta para regulación positiva
    positive_query = """
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX sch: <http://schema.org/>

    SELECT DISTINCT ?gene_name ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) ?evidence_level ?definition
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/prot> {
            ?tfac skos:prefLabel "%s" .
        }
        GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
            ?tfac obo:RO_0002429 ?gene .
        }
        GRAPH <http://rdf.biogateway.eu/graph/gene> {
            ?gene skos:prefLabel ?gene_name .
        }
        GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
            ?s rdfs:subject ?tfac ; 
               rdfs:predicate ?relation ; 
               rdfs:object ?gene ;
               skos:definition ?definition .
            ?uri rdfs:type ?s .
            OPTIONAL { ?uri sio:SIO_000772 ?articles . }
            OPTIONAL { ?uri sio:SIO_000253 ?database . }
            OPTIONAL { ?uri sch:evidenceLevel ?evidence_level. }
        }
    }
    """ % (tfac)
    
    positive_results = data_processing(positive_query)
    if regulation_type == "positive":
        positive_results = [entry for entry in positive_results if "involved in positive regulation" in entry['definition']]
        if not positive_results:
            return "No data available on positive regulation of the introduced trasncription factor. Use the ‘all’ option to search for regulatory information without specifying the type."

    combined_positive_results = defaultdict(lambda: {"gene_name": "", "database": set(), "articles": set(), "evidence_level": "", "definition": ""})

    # Llenar el diccionario combinando artículos
    for entry in positive_results:
        key = (entry['gene_name'], entry['evidence_level'], entry['definition'])
        combined_positive_results[key]['gene_name'] = entry['gene_name']
        combined_positive_results[key]['evidence_level'] = entry['evidence_level']
        combined_positive_results[key]['definition'] = entry['definition']
        combined_positive_results[key]['database'].add(entry['database'])
        if 'articles' in entry:
            combined_positive_results[key]['articles'].add(entry['articles'])

    # Convertir el diccionario de vuelta a una lista, uniendo y ordenando los artículos y las bases de datos
    final_positive_results = []
    for entry in combined_positive_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles'])) if entry['articles'] else ''
        entry['database'] = '; '.join(sorted(entry['database']))
        final_positive_results.append(entry)
    results_sorted_positive = sorted(final_positive_results, key=lambda x: x['gene_name'])

    # Consulta para regulación negativa
    negative_query = """
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX sch: <http://schema.org/>

    SELECT DISTINCT ?gene_name ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) ?evidence_level ?definition
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/prot> {
            ?tfac skos:prefLabel "%s" .
        }
        GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
            ?tfac obo:RO_0002430 ?gene .
        }
        GRAPH <http://rdf.biogateway.eu/graph/gene> {
            ?gene skos:prefLabel ?gene_name .
        }
        GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
            ?s rdfs:subject ?tfac ; 
               rdfs:predicate ?relation ; 
               rdfs:object ?gene ;
               skos:definition ?definition .
            ?uri rdfs:type ?s .
            OPTIONAL { ?uri sio:SIO_000772 ?articles . }
            OPTIONAL { ?uri sio:SIO_000253 ?database . }
            OPTIONAL { ?uri sch:evidenceLevel ?evidence_level. }
        }
    }
    """ % (tfac)
    
    negative_results = data_processing(negative_query)
    if regulation_type == "negative":
        negative_results = [entry for entry in negative_results if "involved in negative regulation" in entry['definition']]
        if not negative_results:
            return "No data available on negative regulation of the introduced transcription factor. Use the ‘all’ option to search for regulatory information without specifying the type."
    combined_negative_results = defaultdict(lambda: {"gene_name": "", "database": set(), "articles": set(), "evidence_level": "", "definition": ""})

    # Llenar el diccionario combinando artículos de resultados negativos
    for entry in negative_results:
        key = (entry['gene_name'], entry['evidence_level'], entry['definition'])
        combined_negative_results[key]['gene_name'] = entry['gene_name']
        combined_negative_results[key]['evidence_level'] = entry['evidence_level']
        combined_negative_results[key]['definition'] = entry['definition']
        combined_negative_results[key]['database'].add(entry['database'])
        if 'articles' in entry:
            combined_negative_results[key]['articles'].add(entry['articles'])

    # Convertir el diccionario de vuelta a una lista, uniendo y ordenando los artículos y las bases de datos
    final_negative_results = []
    for entry in combined_negative_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles'])) if entry['articles'] else ''
        entry['database'] = '; '.join(sorted(entry['database']))
        final_negative_results.append(entry)
    results_sorted_negative = sorted(final_negative_results, key=lambda x: x['gene_name'])

    # Consultar general si ambos resultados están vacíos
    if not positive_results and not negative_results and regulation_type == "all":
        general_query = """
        PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX sch: <http://schema.org/>
        SELECT DISTINCT ?gene_name ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) ?evidence_level ?definition
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?tfac skos:prefLabel "%s" .
            }
            GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
                ?s rdfs:subject ?tfac ;
                   rdfs:object ?gene .
            }
            GRAPH <http://rdf.biogateway.eu/graph/gene> {
                ?gene skos:prefLabel ?gene_name .
            }
            GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
                ?s rdfs:subject ?tfac ; 
                   rdfs:predicate ?relation ; 
                   rdfs:object ?gene ;
                   skos:definition ?definition .
                ?uri rdfs:type ?s .
                OPTIONAL { ?uri sio:SIO_000772 ?articles . }
                OPTIONAL { ?uri sio:SIO_000253 ?database . }
                OPTIONAL { ?uri sch:evidenceLevel ?evidence_level. }
            }
        }
        """ % (tfac)
        
        general_results = data_processing(general_query)
        if not general_results:
            return "No data available for the introduced transcription factor or you may have introduced an instance that is not a transcription factor. Check your data type with type_data function."

        combined_results = defaultdict(lambda: {"gene_name": "", "database": set(), "articles": set(), "evidence_level": "", "definition": ""})
        for entry in general_results:
            key = (entry['gene_name'], entry['evidence_level'], entry['definition'])
            combined_results[key]['gene_name'] = entry['gene_name']
            combined_results[key]['evidence_level'] = entry['evidence_level']
            combined_results[key]['definition'] = entry['definition']
            combined_results[key]['database'].add(entry['database'])
            combined_results[key]['articles'].add(entry['articles'])
        
        final_general_results = []
        for entry in combined_results.values():
            entry['articles'] = '; '.join(sorted(entry['articles']))
            entry['database'] = '; '.join(sorted(entry['database']))
            final_general_results.append(entry)
        
        results_sorted_general = sorted(final_general_results, key=lambda x: x['gene_name'])
        return "Genes related with the selected transcription factor:", results_sorted_general
    # Retornar resultados según el tipo de regulación
    if regulation_type == "positive":
        return "Positive regulation results:", results_sorted_positive
    elif regulation_type == "negative":
        return "Negative regulation results:", results_sorted_negative
    else:
        return "Positive regulation results:", results_sorted_positive, "Negative regulation results:", results_sorted_negative


def gene2tfac(gene, regulation_type="all"):
    endpoint_sparql = sparql_endpoint

    # Consulta para regulación positiva
    positive_query = """
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX sch: <http://schema.org/>

    SELECT DISTINCT ?tfac_name ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)  ?evidence_level ?definition
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/gene> {
                ?gene skos:prefLabel "%s" .
            }
        GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
                ?tfac obo:RO_0002429 ?gene .
            }
        GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?tfac skos:prefLabel ?tfac_name .
            }
            GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
                ?s rdfs:subject ?tfac ; 
                   rdfs:predicate ?relation ; 
                   rdfs:object ?gene ;
                   skos:definition ?definition .
               ?uri rdfs:type ?s .
                OPTIONAL { ?uri  sio:SIO_000772 ?articles . }
                OPTIONAL { ?uri sio:SIO_000253 ?database . }
                OPTIONAL { ?uri   sch:evidenceLevel ?evidence_level. }
            }
    }
    """ % (gene)
    
    # Procesamiento de resultados positivos
    positive_results = data_processing(positive_query)
    if regulation_type == "positive":
        positive_results = [entry for entry in positive_results if "involved in positive regulation" in entry['definition']]
        if not positive_results:
            return "No data available on positive regulation of the introduced gene. Use the ‘all’ option to search for regulatory information without specifying the type."
    
    # Combina resultados positivos
    combined_positive_results = defaultdict(lambda: {"tfac_name": "", "database": set(), "articles": set(), "evidence_level": "", "definition": ""})
    for entry in positive_results:
        key = (entry['tfac_name'], entry['evidence_level'], entry['definition'])
        combined_positive_results[key]['tfac_name'] = entry['tfac_name']
        combined_positive_results[key]['evidence_level'] = entry['evidence_level']
        combined_positive_results[key]['definition'] = entry['definition']
        if entry.get('database'):
            combined_positive_results[key]['database'].add(entry['database'])
        if entry.get('articles'):
            combined_positive_results[key]['articles'].add(entry['articles'])
    
    # Convertir lista consolidada y ordenada de positivos
    final_positive_results = []
    for entry in combined_positive_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles'])) if entry['articles'] else ''
        entry['database'] = '; '.join(sorted(entry['database'])) if entry['database'] else ''
        final_positive_results.append(entry)
    results_sorted_positive = sorted(final_positive_results, key=lambda x: x['tfac_name'])

    # Consulta para regulación negativa
    negative_query = """
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX sch: <http://schema.org/>

    SELECT DISTINCT ?tfac_name ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)  ?evidence_level ?definition
    WHERE {
        GRAPH <http://rdf.biogateway.eu/graph/gene> {
                ?gene skos:prefLabel "%s" .
            }
        GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
                ?tfac obo:RO_0002430 ?gene .
            }
        GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?tfac skos:prefLabel ?tfac_name .
            }
            GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
                ?s rdfs:subject ?tfac ; 
                   rdfs:predicate ?relation ; 
                   rdfs:object ?gene ;
                   skos:definition ?definition .
               ?uri rdfs:type ?s .
                OPTIONAL { ?uri  sio:SIO_000772 ?articles . }
                OPTIONAL { ?uri sio:SIO_000253 ?database . }
                OPTIONAL { ?uri   sch:evidenceLevel ?evidence_level. }
            }
    }
    """ % (gene)
    
    # Procesamiento de resultados negativos
    negative_results = data_processing(negative_query)
    if regulation_type == "negative":
        negative_results = [entry for entry in negative_results if "involved in negative regulation" in entry['definition']]
        if not negative_results:
            return "No data available on negative regulation of the introduced gene. Use the ‘all’ option to search for regulatory information without specifying the type."
    
    # Combina resultados negativos
    combined_negative_results = defaultdict(lambda: {"tfac_name": "", "database": set(), "articles": set(), "evidence_level": "", "definition": ""})
    for entry in negative_results:
        key = (entry['tfac_name'], entry['evidence_level'], entry['definition'])
        combined_negative_results[key]['tfac_name'] = entry['tfac_name']
        combined_negative_results[key]['evidence_level'] = entry['evidence_level']
        combined_negative_results[key]['definition'] = entry['definition']
        if entry.get('database'):
            combined_negative_results[key]['database'].add(entry['database'])
        if entry.get('articles'):
            combined_negative_results[key]['articles'].add(entry['articles'])
    
    # Convertir lista consolidada y ordenada de negativos
    final_negative_results = []
    for entry in combined_negative_results.values():
        entry['articles'] = '; '.join(sorted(entry['articles'])) if entry['articles'] else ''
        entry['database'] = '; '.join(sorted(entry['database'])) if entry['database'] else ''
        final_negative_results.append(entry)
    results_sorted_negative = sorted(final_negative_results, key=lambda x: x['tfac_name'])

    # Consulta general si no hay resultados
    if not positive_results and not negative_results and regulation_type == "all":
        general_query = """
        PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX sch: <http://schema.org/>
        SELECT DISTINCT ?tfac_name ?database (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles)  ?evidence_level ?definition
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/gene> {
                ?gene skos:prefLabel "%s" .
            }
            GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
                ?s rdfs:object ?gene ;
                    rdfs:subject ?tfac .
            }
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?tfac skos:prefLabel ?tfac_name
            }
            GRAPH <http://rdf.biogateway.eu/graph/tfac2gene> {
                ?s rdfs:subject ?tfac ; 
                   rdfs:predicate ?relation ; 
                   rdfs:object ?gene ;
                   skos:definition ?definition .
               ?uri rdfs:type ?s .
                OPTIONAL { ?uri  sio:SIO_000772 ?articles . }
                OPTIONAL { ?uri sio:SIO_000253 ?database . }
                OPTIONAL { ?uri   sch:evidenceLevel ?evidence_level. }
            }
        }
        """ % (gene)
        
        general_results = data_processing(general_query)
        if not general_results:
            return "No data available for the introduced gene or you may have introduced an instance that is not a gene. Check your data type with type_data function."
        
        # Procesar resultados generales
        combined_general_results = defaultdict(lambda: {"tfac_name": "", "database": set(), "articles": set(), "evidence_level": "", "definition": ""})
        for entry in general_results:
            key = (entry['tfac_name'], entry['evidence_level'], entry['definition'])
            combined_general_results[key]['tfac_name'] = entry['tfac_name']
            combined_general_results[key]['evidence_level'] = entry['evidence_level']
            combined_general_results[key]['definition'] = entry['definition']
            if entry.get('database'):
                combined_general_results[key]['database'].add(entry['database'])
            if entry.get('articles'):
                combined_general_results[key]['articles'].add(entry['articles'])

        final_general_results = []
        for entry in combined_general_results.values():
            entry['articles'] = '; '.join(sorted(entry['articles'])) if entry['articles'] else ''
            entry['database'] = '; '.join(sorted(entry['database'])) if entry['database'] else ''
            final_general_results.append(entry)
        results_sorted_general = sorted(final_general_results, key=lambda x: x['tfac_name'])
        return "Transcription factors related with the selected gene:", results_sorted_general

    # Retornar resultados según el tipo de regulación
    if regulation_type == "positive":
        return "Positive regulation results:", results_sorted_positive
    elif regulation_type == "negative":
        return "Negative regulation results:", results_sorted_negative
    else:
        return "Positive regulation results:", results_sorted_positive, "Negative regulation results:", results_sorted_negative


            
def prot2prot(protein):
    endpoint_sparql = sparql_endpoint
    query="""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sch: <http://schema.org/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT  ?prot_label  ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) ?evidence_level ?interaction_details
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:prefLabel "%s" .
                }
            GRAPH <http://rdf.biogateway.eu/graph/prot2prot> {
                    ?prot obo:RO_0002436 ?prot2 .
                    
            }
                GRAPH <http://rdf.biogateway.eu/graph/prot2prot> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?prot2 ;
                         skos:prefLabel ?relation_label .

            }
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot2 skos:prefLabel ?prot_label 
                       .

            }
    BIND(IRI(CONCAT(STR(?uri), "#intact")) AS ?uri_with_intact)
    GRAPH <http://rdf.biogateway.eu/graph/prot2prot> {
        ?uri_with_intact sio:SIO_000772 ?articles ;
                      sio:SIO_000253 ?database ;
                      sch:evidenceLevel ?evidence_level ;
                      obo:BFO_0000050 ?interaction_details .
    }
        }
    """ %(protein)
    results=data_processing(query)
        
    if len(results) == 0:
        query_alt_label="""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX sch: <http://schema.org/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT  ?prot_label  ?relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) ?evidence_level ?interaction_details
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot skos:altLabel "%s" .
                    }

                GRAPH <http://rdf.biogateway.eu/graph/prot2prot> {
                        ?prot obo:RO_0002436 ?prot2 .
                        
                }
                    GRAPH <http://rdf.biogateway.eu/graph/prot2prot> {
                        ?uri rdf:subject ?prot ;
                             rdf:predicate ?relation ;
                             rdf:object ?prot2 ;
                             skos:prefLabel ?relation_label .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot2 skos:prefLabel ?prot_label 
                           .
    
                }
        BIND(IRI(CONCAT(STR(?uri), "#intact")) AS ?uri_with_intact)
        GRAPH <http://rdf.biogateway.eu/graph/prot2prot> {
            ?uri_with_intact sio:SIO_000772 ?articles ;
                          sio:SIO_000253 ?database ;
                          sch:evidenceLevel ?evidence_level ;
                          obo:BFO_0000050 ?interaction_details .
        }
        }
        """ %(protein)
        results=data_processing(query_alt_label)

    combined_results = defaultdict(lambda: {"prot_label": "", "relation_label": "", "database": "", "evidence_level": "", "articles": set(), "interaction_details": set()})
    if not results:
         return "No data available for the introduced protein or you may have introduced an instance that is not a protein. Check your data type with type_data function."
    
    # Llenar el diccionario combinando artículos

    for entry in results:
        key = (entry['prot_label'], entry['relation_label'], entry['database'], entry['evidence_level'])
        combined_results[key]['prot_label'] = entry['prot_label']
        combined_results[key]['relation_label'] = entry['relation_label']
        combined_results[key]['database'] = entry['database']
        combined_results[key]['evidence_level'] = entry['evidence_level']
        combined_results[key]['articles'].add(entry['articles'])
        combined_results[key]['interaction_details'].add(entry['interaction_details'])

    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(entry['articles'])
        entry['interaction_details'] = '; '.join(entry['interaction_details'])
        final_results.append(entry)
    results_sorted = sorted(final_results, key=lambda x: x['prot_label'])
    return results_sorted
    
def prot2ortho (protein):
    endpoint_sparql = sparql_endpoint
    query="""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sch: <http://schema.org/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
    
    SELECT DISTINCT ?prot_label ?orthology_relation_label ?taxon ?common_names 
      (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) ?orthology_details
    WHERE {
        {
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?prot skos:prefLabel "%s" .
            }
            GRAPH <http://rdf.biogateway.eu/graph/ortho> {
                ?uri rdf:object ?prot ;
                     rdf:predicate ?relation ;
                     rdf:subject ?prot2 ;
                     skos:prefLabel ?orthology_relation_label .
            }
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?prot2 skos:prefLabel ?prot_label ;
                       obo:RO_0002162 ?ncbi_taxon .
            }
        }
        UNION
        {
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?prot2 skos:prefLabel "%s" .
            }
            GRAPH <http://rdf.biogateway.eu/graph/ortho> {
                ?uri rdf:subject ?prot2 ;
                     rdf:predicate ?relation ;
                     rdf:object ?prot ;
                     skos:prefLabel ?orthology_relation_label .
            }
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?prot skos:prefLabel ?prot_label ;
                      obo:RO_0002162 ?ncbi_taxon .
            }
        }
        GRAPH <http://rdf.biogateway.eu/graph/taxon> {
            ?ncbi_taxon rdfs:label ?taxon ;
                        oboowl:hasExactSynonym ?common_names .
        }
        BIND(IRI(CONCAT(STR(?uri), "#orthodb")) AS ?uri_with_orthodb)
        GRAPH <http://rdf.biogateway.eu/graph/ortho> {
            ?uri_with_orthodb sio:SIO_000253 ?database ;
                              obo:BFO_0000050 ?orthology_details .
        }
    }
    """ %(protein,protein)
    results=data_processing(query)
        
    if len(results) == 0:
        query_alt_label="""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX sch: <http://schema.org/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
        
        SELECT DISTINCT ?prot_label ?orthology_relation_label ?taxon ?common_names 
          (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) ?orthology_details
        WHERE {
            {
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:altLabel "%s" .
                }
                GRAPH <http://rdf.biogateway.eu/graph/ortho> {
                    ?uri rdf:object ?prot ;
                         rdf:predicate ?relation ;
                         rdf:subject ?prot2 ;
                         skos:prefLabel ?orthology_relation_label .
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot2 skos:prefLabel ?prot_label ;
                           obo:RO_0002162 ?ncbi_taxon .
                }
            }
            UNION
            {
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?prot2 skos:altLabel "%s" .
            }
            GRAPH <http://rdf.biogateway.eu/graph/ortho> {
                ?uri rdf:subject ?prot2 ;
                     rdf:predicate ?relation ;
                     rdf:object ?prot ;
                     skos:prefLabel ?orthology_relation_label .
            }
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                ?prot skos:prefLabel ?prot_label ;
                      obo:RO_0002162 ?ncbi_taxon .
                }
            }
            GRAPH <http://rdf.biogateway.eu/graph/taxon> {
                ?ncbi_taxon rdfs:label ?taxon ;
                            oboowl:hasExactSynonym ?common_names .
            }
            BIND(IRI(CONCAT(STR(?uri), "#orthodb")) AS ?uri_with_orthodb)
            GRAPH <http://rdf.biogateway.eu/graph/ortho> {
                ?uri_with_orthodb sio:SIO_000253 ?database ;
                                  obo:BFO_0000050 ?orthology_details .
            }
        }
        """ %(protein, protein)
        results=data_processing(query_alt_label)
    combined_results = defaultdict(lambda: {"prot_label": "", "orthology_relation_label": "", "taxon": "", "common_names": set(),"database": "", "orthology_details": set()})
    if not results:
         return "No data available for the introduced protein or you may have introduced an instance that is not a protein. Check your data type with type_data function."
    
    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['prot_label'], entry['orthology_relation_label'], entry['taxon'], entry['database'])
        combined_results[key]['prot_label'] = entry['prot_label']
        combined_results[key]['orthology_relation_label'] = entry['orthology_relation_label']
        combined_results[key]['taxon'] = entry['taxon']
        combined_results[key]['database'] = entry['database']
        combined_results[key]['common_names'].add(entry['common_names'])
        combined_results[key]['orthology_details'].add(entry['orthology_details'])

    # Convertir el diccionario de vuelta a una lista, uniendo los artículos
    final_results = []
    for entry in combined_results.values():
        entry['common_names'] = '; '.join(entry['common_names'])
        entry['orthology_details'] = '; '.join(entry['orthology_details'])
        final_results.append(entry)
    results_sorted = sorted(final_results, key=lambda x: x['prot_label'])
    return results_sorted
    
def prot_regulates(protein, regulation_type="all"):
    endpoint_sparql = sparql_endpoint
    query="""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sch: <http://schema.org/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT  ?prot_label  ?definition ?regulatory_relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) ?evidence_level 
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:prefLabel "%s" .
      
          }
                GRAPH <http://rdf.biogateway.eu/graph/reg2targ> {
                    ?uri rdf:subject ?prot ;
                         rdf:predicate ?relation ;
                         rdf:object ?prot2 ;
                         skos:definition ?definition ;
                         skos:prefLabel ?regulatory_relation_label .

            }
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot2 skos:prefLabel ?prot_label 
                       .

            }
    BIND(IRI(CONCAT(STR(?uri), "#signor")) AS ?uri_with_signor)
    GRAPH <http://rdf.biogateway.eu/graph/reg2targ> {
        ?uri_with_signor sio:SIO_000772 ?articles ;
                      sio:SIO_000253 ?database ;
                      sch:evidenceLevel ?evidence_level .
    }
        }
    """ %(protein)
    results=data_processing(query)
        
    if len(results) == 0:
        query_alt_label="""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX sch: <http://schema.org/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT  ?prot_label  ?definition ?regulatory_relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) ?evidence_level 
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot skos:altLabel "%s" .
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/reg2targ> {
                        ?uri rdf:subject ?prot ;
                             rdf:predicate ?relation ;
                             rdf:object ?prot2 ;
                             skos:definition ?definition ;
                             skos:prefLabel ?regulatory_relation_label .
 
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot2 skos:prefLabel ?prot_label 
                           .
    
                }
        BIND(IRI(CONCAT(STR(?uri), "#signor")) AS ?uri_with_signor)
        GRAPH <http://rdf.biogateway.eu/graph/reg2targ> {
            ?uri_with_signor sio:SIO_000772 ?articles ;
                          sio:SIO_000253 ?database ;
                          sch:evidenceLevel ?evidence_level .
        }
            } 
        """ %(protein)
        results=data_processing(query_alt_label)

    combined_results = defaultdict(lambda: {"prot_label": "", "definition": "",  "regulatory_relation_label": "", "database": "", "evidence_level": "", "articles": set()})
    if not results:
         return "No data available for the introduced protein or you may have introduced an instance that is not a protein. Check your data type with type_data function."
    
    # Llenar el diccionario combinando artículos
    for entry in results:
        key = (entry['prot_label'], entry['definition'], entry['regulatory_relation_label'], entry['database'], entry['evidence_level'])
 
        combined_results[key]['prot_label'] = entry['prot_label']
        combined_results[key]['definition'] = entry['definition']
        combined_results[key]['regulatory_relation_label'] = entry['regulatory_relation_label']
        combined_results[key]['database'] = entry['database']
        combined_results[key]['evidence_level'] = entry['evidence_level']
        combined_results[key]['articles'].add(entry['articles'])

    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(entry['articles'])
        final_results.append(entry)
            # Filtrar por el tipo de regulación: "positive", "negative" o "all"
    if regulation_type == "positive":
        final_results = [entry for entry in final_results if "positive regulation" in entry['definition']]
        if not final_results:
            return "No data available on positive regulation of the introduced gene. Use the ‘all’ option to search for regulatory information without specifying the type."
    elif regulation_type == "negative":
        final_results = [entry for entry in final_results if "negative regulation" in entry['definition']]
        if not final_results:
            return "No data available on negative regulation of the introduced gene. Use the ‘all’ option to search for regulatory information without specifying the type."
    results_sorted = sorted(final_results, key=lambda x: x['prot_label'])
    seen_labels = set()
    unique_proteins = []
    for protein in results_sorted:
        if protein['prot_label'] not in seen_labels:
            seen_labels.add(protein['prot_label'])
            unique_proteins.append(protein)
    return unique_proteins       



def prot_regulated_by(protein,regulation_type="all"):
    endpoint_sparql = sparql_endpoint
    query="""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sch: <http://schema.org/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT  ?prot_label  ?definition ?regulatory_relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) ?evidence_level 
        WHERE {
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot skos:prefLabel "%s" .
      
          }
                GRAPH <http://rdf.biogateway.eu/graph/reg2targ> {
                    ?uri rdf:object ?prot ;
                         rdf:predicate ?relation ;
                         rdf:subject ?prot2 ;
                         skos:definition ?definition ;
                         skos:prefLabel ?regulatory_relation_label .

            }
            GRAPH <http://rdf.biogateway.eu/graph/prot> {
                    ?prot2 skos:prefLabel ?prot_label 
                       .

            }
    BIND(IRI(CONCAT(STR(?uri), "#signor")) AS ?uri_with_signor)
    GRAPH <http://rdf.biogateway.eu/graph/reg2targ> {
        ?uri_with_signor sio:SIO_000772 ?articles ;
                      sio:SIO_000253 ?database ;
                      sch:evidenceLevel ?evidence_level .
    
}

        }
    """ %(protein)
    results=data_processing(query)
        
    if len(results) == 0:
        query_alt_label="""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX sch: <http://schema.org/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX sio: <http://semanticscience.org/resource/>
        PREFIX oboowl: <http://www.geneontology.org/formats/oboInOwl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT  ?prot_label  ?definition ?regulatory_relation_label (REPLACE(STR(?database), "http://identifiers.org/", "") AS ?database) (REPLACE(STR(?articles), "http://identifiers.org/", "") AS ?articles) ?evidence_level 
            WHERE {
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot skos:altLabel "%s" .
                    }
                    GRAPH <http://rdf.biogateway.eu/graph/reg2targ> {
                        ?uri rdf:object ?prot ;
                             rdf:predicate ?relation ;
                             rdf:subject ?prot2 ;
                             skos:definition ?definition ;
                             skos:prefLabel ?regulatory_relation_label .
 
                }
                GRAPH <http://rdf.biogateway.eu/graph/prot> {
                        ?prot2 skos:prefLabel ?prot_label 
                           .
    
                }
        BIND(IRI(CONCAT(STR(?uri), "#signor")) AS ?uri_with_signor)
        GRAPH <http://rdf.biogateway.eu/graph/reg2targ> {
            ?uri_with_signor sio:SIO_000772 ?articles ;
                          sio:SIO_000253 ?database ;
                          sch:evidenceLevel ?evidence_level .
        }
            } 
        """ %(protein)
        results=data_processing(query_alt_label)

    combined_results = defaultdict(lambda: {"prot_label": "", "definition": "",  "regulatory_relation_label": "", "database": "", "evidence_level": "", "articles": set()})
    if not results:
         return "No data available for the introduced protein or you may have introduced an instance that is not a protein. Check your data type with type_data function."
    
    for entry in results:
        key = (entry['prot_label'], entry['definition'], entry['regulatory_relation_label'], entry['database'], entry['evidence_level'])
 

        combined_results[key]['prot_label'] = entry['prot_label']
        combined_results[key]['definition'] = entry['definition']
        combined_results[key]['regulatory_relation_label'] = entry['regulatory_relation_label']
        combined_results[key]['database'] = entry['database']
        combined_results[key]['evidence_level'] = entry['evidence_level']
        combined_results[key]['articles'].add(entry['articles'])

    final_results = []
    for entry in combined_results.values():
        entry['articles'] = '; '.join(entry['articles'])
        final_results.append(entry)
                    # Filtrar por el tipo de regulación: "positive", "negative" o "all"
    if regulation_type == "positive":
        final_results = [entry for entry in final_results if "positive regulation" in entry['definition']]
        if not final_results:
            return "No data available on positive regulation of the introduced gene. Use the ‘all’ option to search for regulatory information without specifying the type."
    elif regulation_type == "negative":
        final_results = [entry for entry in final_results if "negative regulation" in entry['definition']]
        if not final_results:
            return "No data available on negative regulation of the introduced gene. Use the ‘all’ option to search for regulatory information without specifying the type."
    results_sorted = sorted(final_results, key=lambda x: x['prot_label'])
    seen_labels = set()
    unique_proteins = []

    for protein in results_sorted:
        if protein['prot_label'] not in seen_labels:
            seen_labels.add(protein['prot_label'])
            unique_proteins.append(protein)
    return unique_proteins    