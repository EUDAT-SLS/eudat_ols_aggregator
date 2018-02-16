# EUDAT Semantic Lookup Service Harvester

This is a prototypical implementation for a service which harvests information about semantic concepts from semantic resources hosted via dedicated repositories. The main goal within EUDAT is to enable interdisciplinary annotation of data with controlled terminology via services such as [EUDAT B2Note](https://github.com/EUDAT-B2NOTE/b2note). For a broader description of the approach see [(Goldfarb & Le Franc, 2017)](http://ceur-ws.org/Vol-1933/paper-7.pdf)

* Definitions


    * Semantic concept: 

        Classes, individuals, concepts or terms serving as building blocks for knowledge organization systems such as ontologies, thesauri or controlled vocabularies. A main requirement is that these entities are identified via a unique ID, usually provided in form of a URI, and should have a clear definition of their meaning.

    * Semantic resource: 

        A collection of Semantic concepts and potential relationships between them, formalized as controlled vocabulary, thesaurus or ontology.

    * Semantic repository: 

        Online repository for uploading, discovering and retrieving semantic resources.

* Implementation

<img align="middle" src="https://raw.githubusercontent.com/EUDAT-SLS/eudat_ols_aggregator/adea9dc6f063b09d6ce4ff3cf1ed45e6bebaac2e/images/basic_workflow.PNG" width="500"/>

<img align="middle" src="https://raw.githubusercontent.com/EUDAT-SLS/eudat_ols_aggregator/adea9dc6f063b09d6ce4ff3cf1ed45e6bebaac2e/images/exampleconfig.PNG"/>

<img align="middle" src="https://raw.githubusercontent.com/EUDAT-SLS/eudat_ols_aggregator/adea9dc6f063b09d6ce4ff3cf1ed45e6bebaac2e/images/DataContainer.PNG" width="300"/>

<img align="middle" src="https://raw.githubusercontent.com/EUDAT-SLS/eudat_ols_aggregator/adea9dc6f063b09d6ce4ff3cf1ed45e6bebaac2e/images/DataContainer_invocation.PNG"/>

Harvesting of Semantic Repositories

* Files:

    * Configuration:

      [repoConfig_noapikey.json](repoConfig_noapikey.json) - Example configuration for three Semantic Repositories EBI-OLS, Bioportal and Agroportal. For the latter two, API keys must be obtained for each and inserted into the respective <YOUR XXXPORTAL API KEY HERE> fields in the json file.

      [mongoConfig.json](mongoConfig.json) - Specify host and port of used MongoDB instance, collections for repositories, classes and instances

      [mandatory.json](mandatory.json) - Specify which fields must be present for a term to be stored into the DB.

    * Code

      [DataContainer.py](DataContainer.py) - Class for handling Semantic Repository descriptions as shown in [(repoConfig_noapikey.json](repoConfig_noapikey.json).

      [MongoConnector.py](MongoConnector.py) - Class for storing terms harvested via [DataContainer.py](DataContainer.py) to MongoDB instance specified via [mongoConfig.json](mongoConfig.json). An instance of this class must be passed to the root DataContainer instance and is reused there.

      [retrieve.py](retrieve.py) - Script for harvesting terms from repositories using the above configuration files and [DataContainer.py](DataContainer.py)


References:

    (Goldfarb & Le Franc, 2017) 
    D. Goldfarb and Y. Le Franc. Enhancing the Discoverability and Interoperability of Multi-Disciplinary Semantic Repositories. In: A. Algergawy, N. Karam, F. Klan, C. Jonquet: Proc. of the 2nd International Workshop on Semantics for Biodiversity co-located with 16th International Semantic Web Conference (ISWC 2017), Vienna, Austria, October 22nd, 2017. CEUR Workshop Proceedings 1933


##########################

Created by Doron Goldfarb, contact: doron.goldfarb@umweltbundesamt.at

(c) 2018, Environment Agency Austria


This work was funded by the European Union via the EUDAT2020 project under grant agreement n.654065
