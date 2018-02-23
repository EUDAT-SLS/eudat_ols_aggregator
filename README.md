# EUDAT Semantic Lookup Service Harvester

# This documentation is work in progress

This is a prototypical implementation for a service which harvests information about semantic concepts from semantic resources hosted via dedicated repositories. The main purpose for this service within EUDAT is to support interdisciplinary annotation of data by providing controlled terminology to services such as [EUDAT B2Note](https://github.com/EUDAT-B2NOTE/b2note). For a broader description of the approach see [(Goldfarb & Le Franc, 2017)](http://ceur-ws.org/Vol-1933/paper-7.pdf)

The service basically consists of a script which consumes a configuration file describing the locations and APIs of Semantic repositories (Currently: BioPortal, AgroPortal and EBI-OLS) in order to harvest the information about the semantic resources and concepts hosted there. The resulting data is written into a database (Currently: MongoDB) in unified form, mainly consisting of concept ID, preferred label, synonyms, description as well as resource and repository level information.

The content of the db can subsequently be fed into a Solr index which can be used for various lookup services. A faceted search preview for the results of the harvesting of BioPortal, AgroPortal and EBI-OLS can be explored at https://bsceudatwp8.bsc.es/termbrowser

# Quickstart

* **Files**:

    * **Configuration:**

      [repoConfig_noapikey.json](repoConfig_noapikey.json) - Example configuration for three Semantic Repositories EBI-OLS, Bioportal and Agroportal. For the latter two, API keys must be obtained for each and inserted into the respective <YOUR XXXPORTAL API KEY HERE> fields in the json file.

      [mongoConfig.json](mongoConfig.json) - Specify host and port of used MongoDB instance, collections for repositories, classes and instances

      [mandatory.json](mandatory.json) - Specify which fields must be present for a term to be stored into the DB.

    * **Code:**

      [DataContainer.py](DataContainer.py) - Class for handling Semantic Repository descriptions as shown in [(repoConfig_noapikey.json](repoConfig_noapikey.json).

      [MongoConnector.py](MongoConnector.py) - Class for storing terms harvested via [DataContainer.py](DataContainer.py) to MongoDB instance specified via [mongoConfig.json](mongoConfig.json). An instance of this class must be passed to the root DataContainer instance and is reused there.

      [retrieve.py](retrieve.py) - Script for harvesting terms from repositories using the above configuration files and [DataContainer.py](DataContainer.py)

    * **Solr related:**

      the [solr directory](solr) contains various items for creating the Solr index.

        * The script [solr_writer.py](solr/solr_writer.py) should be used for populating a Solr core with information from the database. 

        * The subdirectory [core_config](solr/core_config) provides the respective configuration files based on a Solr 5.5.3 installation. The [core_config/conf/schema.xml](solr/core_config/conf/schema.xml) file and the associated stopword lists are modified/reused from the Solr configuration provided by [EBI-OLS](https://github.com/EBISPOT/OLS/tree/master/ols-solr/src/main/solr-5-config/ontology/conf)

        *  The subdirectory [core_config/conf/velocity](solr/core_config/conf/velocity) contains Velocity templates for rendering the faceted view prototype.

* **Requirements:**

    * **MongoDB:**

      A running MongoDB installation is required, its adress etc. should be configured in [mongoConfig.json](mongoConfig.json). A dedicated database with four collections must be explicitely created. There are two pairs of collections, one for classes, one for instances. Each pair consists of one collection for "current" classes/instances and one for "old" ones. In each harvesting run, classes/instances with changed data are moved to the "old" collection and overwritten in the "current" one. The default configuration in [mongoConfig.json](mongoConfig.json) assumes the following: A database EUDAT_OLS with collections for classes: "termcollection" and "oldtermcollection" and instances: "instancecollection" and "oldinstancecollection"

    * **Repository configuration:**

      The list of configured repositories can be passed as file such as in [repoConfig_noapikey.json](repoConfig_noapikey.json) or stored in the MongoDB in a dedicated collection, which can also be specified via [mongoConfig.json](mongoConfig.json)

    * **Solr installation:**

    The provided configuration files and Velocity templates were tested on a Solr 5.5.3 installation. They assume a Solr core named "termcollection" and should be put into the respective location (e.g. /var/solr/data/termcollection/...). The Velocity templates require some static files (css, img, js) which are located in the same directory but must be moved to the root solr server directory into a subdirectory called "termbrowser_resources" (e.g. [SOLR_HOME]/server/solr-webapp/webapp/termbrowser_resources/[css|img|js]/*). 
 

    * **System configuration:**

      It is highly advisable to have sufficient RAM available on the machine running the harvester, EBI-OLS, Bioportal and Agroportal together yield about 15M classes/instances.

* **Invocation**

    If the repository configuration shall be passed as file:

    ./retrieve.py -c repoConfig.json -m mandatory.json -M mongoConfig.json   

# Documentation


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



References:

    (Goldfarb & Le Franc, 2017) 
    D. Goldfarb and Y. Le Franc. Enhancing the Discoverability and Interoperability of Multi-Disciplinary Semantic Repositories. In: A. Algergawy, N. Karam, F. Klan, C. Jonquet: Proc. of the 2nd International Workshop on Semantics for Biodiversity co-located with 16th International Semantic Web Conference (ISWC 2017), Vienna, Austria, October 22nd, 2017. CEUR Workshop Proceedings 1933


##########################

Created by Doron Goldfarb, contact: doron.goldfarb@umweltbundesamt.at

(c) 2018, Environment Agency Austria


This work was funded by the European Union via the EUDAT2020 project under grant agreement n.654065
