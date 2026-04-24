
# PyBioGateway <img src="figures/PyBioGateway_logo.png" align="right" width="100" />

<!-- badges: start -->
<!-- badges: end -->

## Overview

PyBioGateway is an Python package that provides programmatic access to BioGateway (https://biogateway.eu), a biological knowledge graph that integrates data from multiple databases across diverse biological domains. The package offers a set of user-friendly functions that abstract users from the SPARQL query language, enabling seamless access to integrated information on genes, proteins, phenotypes, cis-regulatory modules, topologically associating domains, Gene Ontology terms, and the relationships among these entities.
A package to perform queries and exploit the data on RStudio is also available on [RBioGateway](https://github.com/tecnomod-um/RBioGateway).

![BGW example](https://github.com/juan-mulero/cisreg/blob/19d2155282f4242dac0f8a076a05679c651cacef/images/UseCases.PNG "Example")

Although BioGateway is a knowledge network focused mainly on human, information about other organisms can also be explored:

| Taxon                                   | Common name                 | Taxon ID |
|-----------------------------------------|-----------------------------|----------|
| *Mus musculus*                          | House mouse                 | 10090    |
| *Arabidopsis thaliana*                  | Thale cress                 | 3702     |
| *Oryza sativa* Japonica Group           | Rice (Asian rice)           | 39947    |
| *Dictyostelium discoideum*              | Social amoeba               | 44689    |
| *Zea mays*                              | Maize (corn)                | 4577     |
| *Caenorhabditis elegans*                | Nematode (roundworm)        | 6239     |
| *Danio rerio*                           | Zebrafish                   | 7955     |
| *Gallus gallus*                         | Chicken                     | 9031     |
| *Sus scrofa*                            | Pig                         | 9823     |
| *Bos taurus*                            | Cattle                      | 9913     |
| *Homo sapiens*                          | Human                       | 9606     |
| *Drosophila melanogaster*               | Fruit fly                   | 7227     |
| *Oryctolagus cuniculus*                 | Rabbit                      | 9986     |
| *Rattus norvegicus*                     | Brown rat                   | 10116    |
| *Saccharomyces cerevisiae* S288C        | Baker’s yeast               | 559292   |
| *Schizosaccharomyces pombe* 972h-       | Fission yeast               | 284812   |
| *Chlamydomonas reinhardtii*             | Green alga                  | 3055     |
| *Plasmodium falciparum* 3D7             | Malaria parasite            | 36329    |
| *Neurospora crassa* OR74A               | Red bread mold              | 367110   |
| *Canis lupus familiaris*                | Dog                         | 9615     |


**Key Features**
- Python Interface: Seamless integration with BioGateway endpoint.
- Reproducible Research: Designed to fit into standard Python bioinformatics workflows.
- R Parity: Implements equivalent functionality to the existing [R package](https://github.com/tecnomod-um/RBioGateway).


## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Functions](#functionalities-overview)
  - [Functions that relate entities](#functions-that-relate-entities)
  - [Functions that extract features](#functions-that-extract-features)
  - [Functions by location aspects](#functions-by-location-aspects)
- [About BioGateway](#about-biogateway)
- [Example of Use Case](#example-of-use-case-detailed)



## Installation

To install the package, use pip after cloning and accessing the repository.

```bash
pip install .
```


## Functionalities overview

Detailed documentation about functions is available [here](./docs/README.md). These can be classified into three main groups:
- Functions that relate entities, that is, different biological domains.
- Functions that extract features from a given entity.
- Functions that extract biological entities by location aspects.

### Functions that relate entities:

| Function              | Input Domain                                  | Output domain                              |
|-----------------------|-----------------------------------------------|--------------------------------------------|
| crm2gene              | Cis-Regulatory Module (enhancer)              | Target gene                                |
| gene2crm              | Gene                                          | Cis-Regulatory Module (enhancer)           |
| crm2tfac              | Cis-Regulatory Module (enhancer)              | Protein (Binding Transcription Factor)     |
| tfac2crm              | Protein (Binding Transcription Factor)        | Cis-Regulatory Module (enhancer)           |
| gene2tfac             | Gene                                          | Protein (regulatory Transcription Factor)  |
| tfac2gene             | Protein (regulatory Transcription Factor)     | Gene                                       |
| crm2phen              | Cis-Regulatory Module (enhancer)              | Phenotype associated                       |
| phen2cm               | Phenotype                                     | Cis-Regulatory Module associated (enhancer)|
| phen2gene             | Phenotype                                     | Gene                                       |
| gene2phen             | Gene                                          | Phenotype                                  |
| gene2prot             | Gene                                          | Protein (encoded)                          |
| prot2gene             | Protein                                       | Gene (encoding)                            |
| bp2prot               | Biological process                            | Protein                                    |
| prot2bp               | Protein                                       | Biological process                         |
| cc2prot               | Cellular component                            | Protein                                    |
| prot2cc               | Protein                                       | Cellular component                         |
| mf2prot               | Molecular function                            | Protein                                    |
| prot2mf               | Protein                                       | Molecular function                         |
| prot_regulated_by     | Protein                                       | Protein (regulatory)                       |
| prot_regulates        | Protein                                       | Protein (regulated)                        |
| prot2prot             | Protein                                       | Protein (molecular interaction)            |
| prot2ortho            | Protein                                       | Protein (orthologous)                      |


### Functions that extract features:

| Function              | Input                                   | Output                                       |
|-----------------------|-----------------------------------------|----------------------------------------------|
| type_data             | Entity                                  | Biological type (for example: Gene, Protein) |
| getGene_info          | Gene                                    | Gene features                                |
| getProtein_info       | Protein                                 | Protein features                             |
| getPhenotye           | label                                   | Phenotypes containing the label              |
| getCRM_info           | CRM                                     | CRM genomic features                         |
| getCRM_add_info       | CRM                                     | CRM evidences                                |
| getTAD_info           | TAD                                     | TAD genomic features                         |
| getTAD_add_info       | TAD                                     | TAD evidences                                |


### Functions by location aspects:

| Function              | Input                                   | Output                                       |
|-----------------------|-----------------------------------------|----------------------------------------------|
| getGenes_by_coord     | Coordinates                             | Genes inside the range                       |
| getCRMs_by_coord      | Coordinates                             | CRMs inside the range                        |
| getTADs_by_coord      | Coordinates                             | TADs inside the range                        |


## About BioGateway

BioGatewya integrates a total of 38 sources indicated below.

**Biological domains and their databases:**
-   **Cis-regulatory modules (CRM)**. Databases (25): CancerEnD, JEME, EnDisease, FANTOM5, FOCS, EnhancerDB, HACER, EnnhancerAtlas 2.0, ChromHMM, Ensembl 109, SEA 3.0, GenoSTAN, SEdb 2.0, scEnhancer, EnhFFL, GeneHancer 4.8, Roadmap, RAEdb, TiED, SCREEN V3, dbSUPER, DiseaseEnhancer, ENdb, Refseq V110, VISTA.
-   **Topological associated domains (TAD)**. Databases (2): 3DGB and TADKB.
-   **Genes**. Databases (1): Uniprot.
-   **Proteins**. Databases (1): Uniprot.
-   **Phenotypes**. Databases (1): Online Mendelian Inheritance in Man (OMIM).
-   **Biological Processes**. Databases (1): Gene Ontology (GO).
-   **Molecular functions**. Databases (1): Gene Ontology (GO).
-   **Cellular components**. Databases (1): Gene Ontology (GO).
-   **Taxa**. Database (1): NCBITaxon Ontology.

**Relationships between biological domains and their databases:**
-   **CRMs and target genes**. Databases (16): CancerEnD, JEME, EnDisease, FANTOM5, FOCS, HACER, EnnhancerAtlas 2.0, SEA 3.0, SEdb 2.0, scEnhancer, EnhFFL, GeneHancer 4.8, dbSUPER, DiseaseEnhancer, ENdb, VISTA.
-   **CRMs and transcription factors (proteins)**. Databases (2): ENdb and EnhFFL.
-   **CRMs and phenotypes**. Databases (3): DiseaseEnhancer, ENdb, EnDisease.
-   **Genes and phenotypes**. Databases (1): Uniprot/OMIM. 
-   **Proteins and biological processes**. Databases (1): Gene Ontology.
-   **Proteins and molecular functions**. Databases (1): Gene Ontology.
-   **Proteins and cellular components**. Databases (1): Gene Ontology.
-   **Protein interactions**. Databases (1): IntAct.
-   **Target genes and transcripcion factors (proteins)**. Databases (3): CollecTRI, TFLink and AGRIS.
-   **Protein-Protein regulatory relations**. Databases (1): Signor.
-   **Orthology proteins**. Databases (1): OrthoDB.

The Molecular Interactions Ontology (MI) and the Biolink model are also included in BioGateway.

The targeted endpoint of BioGateway is available at [https://semantics.inf.um.es/biogateway](https://semantics.inf.um.es/biogateway), using SPARQL language.

An interactive and user-friendly web application is also available at [https://semantics.inf.um.es/intuition_biogateway](https://semantics.inf.um.es/intuition_biogateway).

The BioGateway network is structured in [RDF](https://www.w3.org/RDF/) graphs, being each graph a different information domain. We distinguish two types of graphs in the network: entity graphs and relation graphs. The first ones aim to model different biological entities, while the second ones model relations between different entities.

![BGW graphs](https://github.com/juan-mulero/cisreg/blob/19d2155282f4242dac0f8a076a05679c651cacef/images/graphs.png "BioGateway network")

The knowledge network of BioGateway has the following graphs:
- crm : Cis Regulatory Modules (CRM). Currently only enhancer sequences, that increase gene transcription levels.
- crm2phen: Relations between CRM and phenotypes.
- crm2gene: Relations between CRM and target genes.
- crm2tfac: Relations between CRM and transcription factors.
- tad : Topologically associating domain. Domains of genome structure and regulation.
- gene : Genes.
- prot : Proteins.
- omim : OMIM ontology (phenotypes, among others).
- go : GO ontology (biological processes, molecular functions and cellular components).
- mi : Molecular Interaction Ontology.
- taxon : NCBI Taxon Ontology.
- gene2phen : Genes - Phenotypes (omim) relations .
- tfac2gene : Relations between transcription factors and their target genes.
- prot2prot : Protein-protein interactions.
- reg2targ : Protein - Protein regulatory relations
- prot2cc : Protein - Celullar components relations.
- prot2bp : Protein - Biological processes relations.
- prot2mf : Protein - Molecular functions relations.
- ortho : Protein-protein orthology relations.  

Supplementary material and tutorials for further exploration of the BioGateway network are available in the [cisreg](https://github.com/juan-mulero/cisreg) repository.


## Example of Use Case detailed

We have one mutation of interest (rs4784227 -> chr16:52565276) and we want to study its possible implications in the regulation of gene expression in human. 

First we will find the enhancers (CRMs) that are located on these coords with the function getCRMs_by_coord.

```python
from PyBioGateway import getCRMs_by_coord, crm2phen, getPhenotype, crm2gene, gene2protein, prot2bp

mutation_position = 52565276

# We define a range around the mutation position (e.g., +/- 1000 bases)
range_start = mutation_position - 12500
range_end = mutation_position + 12500

#Now we use the function to get CRMs in the defined range
crms = getCRMs_by_coord("chr-16", range_start, range_end)

# We will count the number of entries in the list
num_entries = len(crms) if isinstance(crms, list) else 0
print(f"Number of CRMs in the specified range: {num_entries}")
```
Number of CRMs in the specified range: 485

We will select some CRMs for continue the study, and we will see if the CRMs are related with any disease using crm2phen function:
```python
for crm in crms:
    crm_name = crm['crm_name']
    phen_results = crm2phen(crm_name)
    if phen_results != ("No data available for the introduced crm or you may have introduced an instance that is not a crm. Check your data type with type_data function."):    
        print(f"CRM: {crm_name}")
        print(f"Phenotypes: {phen_results}\n")

print(getPhenotype("114480"))
```
CRM: crm/CRMHS00000005858
Phenotypes: [{'phen_id': 'OMIM/114480', 'database': 'http://biocc.hrbmu.edu.cn/DiseaseEnhancer/; http://health.tsinghua.edu.cn/jianglab/endisease/', 'articles': 'pubmed/23001124'}, {'phen_id': 'MESH/D001943', 'database': 'http://biocc.hrbmu.edu.cn/DiseaseEnhancer/; http://health.tsinghua.edu.cn/jianglab/endisease/', 'articles': 'pubmed/23001124'}, {'phen_id': 'DOID/DOID_1612', 'database': 'http://biocc.hrbmu.edu.cn/DiseaseEnhancer/; http://health.tsinghua.edu.cn/jianglab/endisease/', 'articles': 'pubmed/23001124'}]
[{'phen_label': 'BREAST CANCER'}]

We get the CRMs that are related to a phenotype, in this case only crm/CRMHS00000005858 is related to a disease, which is Breast cancer (OMIM:114480).

We are going now to search if our CRM has any target gene using crm2gene function:
```python
genes=crm2gene("crm/CRMHS00000005858")
print(genes)
```
[{'gene_name': 'TOX3', 'database': 'http://biocc.hrbmu.edu.cn/DiseaseEnhancer/; http://health.tsinghua.edu.cn/jianglab/endisease/', 'articles': 'pubmed/23001124'}]

The gene TOX3 is related to our CRM, now we can find which proteins are encoded by this gene in *Homo sapiens* with gene2protein function:
```python
protein=gene2protein("TOX3","Homo sapiens")
print(protein)
```
[{'prot_name': 'H3BTZ9_HUMAN'}, {'prot_name': 'J3QQQ6_HUMAN'}, {'prot_name': 'TOX3_HUMAN'}]

Finally we want to know in which biological process are involved these proteins. We use prot2bp function:

```python
for prot in protein:
    prot_name=prot['prot_name']
    bp_results=prot2bp(prot_name)
    print(f"Protein {prot_name}")
    print(f"Biological process: {bp_results}\n")
```
Protein H3BTZ9_HUMAN
Biological process: No data available for the introduced protein or you may have introduced an instance that is not a protein. Check your data type with type_data function.

Protein J3QQQ6_HUMAN
Biological process: No data available for the introduced protein or you may have introduced an instance that is not a protein. Check your data type with type_data function.

Protein TOX3_HUMAN
Biological process: [{'bp_id': 'GO:0006357', 'bp_label': 'regulation of transcription by RNA polymerase II', 'relation_label': 'O15405--GO:0006357', 'database': 'goa/', 'articles': 'pubmed/21873635'}, {'bp_id': 'GO:0042981', 'bp_label': 'regulation of apoptotic process', 'relation_label': 'O15405--GO:0042981', 'database': 'goa/', 'articles': 'pubmed/21172805'}, {'bp_id': 'GO:0043524', 'bp_label': 'negative regulation of neuron apoptotic process', 'relation_label': 'O15405--GO:0043524', 'database': 'goa/', 'articles': 'pubmed/21172805'}, {'bp_id': 'GO:0045944', 'bp_label': 'positive regulation of transcription by RNA polymerase II', 'relation_label': 'O15405--GO:0045944', 'database': 'goa/', 'articles': 'pubmed/21172805'}]

As we can see, TOX3_HUMAN protein is related with regulation of apoptotic process, regulation of transcription by RNA polymerase II, negative regulation of neuron apoptotic process and positive regulation of transcription by RNA polymerase II. 


## Development Status
This package is currently under development within the [TECNOMOD](https://github.com/tecnomod-um) group from University of Murcia, Spain.


## License
MIT License


## Citation

Mulero-Hernández, J., Mironov, V., Miñarro-Giménez, J. A., Kuiper, M., & Fernández-Breis, J. T. (2024). Integration of chromosome locations and functional aspects of enhancers and topologically associating domains in knowledge graphs enables versatile queries about gene regulation. Nucleic Acids Research, 52(15), e69-e69, doi: https://doi.org/10.1093/nar/gkae566
```
@article{mulero2024integration,
  title={Integration of chromosome locations and functional aspects of enhancers and topologically associating domains in knowledge graphs enables versatile queries about gene regulation},
  author={Mulero-Hern{\'a}ndez, Juan and Mironov, Vladimir and Mi{\~n}arro-Gim{\'e}nez, Jos{\'e} Antonio and Kuiper, Martin and Fern{\'a}ndez-Breis, Jesualdo Tom{\'a}s},
  journal={Nucleic Acids Research},
  volume={52},
  number={15},
  pages={e69--e69},
  year={2024},
  publisher={Oxford University Press},
  doi={10.1093/nar/gkae566}
}
```

Antezana, E., Blondé, W., Egaña, M., Rutherford, A., Stevens, R., De Baets, B., ... & Kuiper, M. (2009). BioGateway: a semantic systems biology tool for the life sciences. BMC bioinformatics, 10(Suppl 10), S11, doi: https://doi.org/10.1186/1471-2105-10-s10-s11
```
@article{antezana2009biogateway,
  title={BioGateway: a semantic systems biology tool for the life sciences},
  author={Antezana, Erick and Blond{\'e}, Ward and Ega{\~n}a, Mikel and Rutherford, Alistair and Stevens, Robert and De Baets, Bernard and Mironov, Vladimir and Kuiper, Martin},
  journal={BMC bioinformatics},
  volume={10},
  number={Suppl 10},
  pages={S11},
  year={2009},
  publisher={Springer},
  doi={10.1186/1471-2105-10-s10-s11}
}
```


## Contact Information
For any inquiries or issues, please contact:

Alberto Hernández-Hidalgo (Developer) - Email: albertoherhid@gmail.com <br>
Juan Mulero-Hernández (Developer) - Email: juan.mulero@um.es <br>
Jesualdo Tomás Fernández-Breis (Principal Investigator) - Email: jfernand@um.es