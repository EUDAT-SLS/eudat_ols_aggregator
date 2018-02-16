# EUDAT Semantic Lookup Service Harvester

This is a prototypical implementation for a service which harvests information about semantic concepts from semantic resources hosted via dedicated repositories. 

* Definitions


    * > Semantic concept: Classes, individuals, concepts or terms serving as building blocks for knowledge organization systems such as ontologies, thesauri or controlled vocabularies. A main requirement is that these entities are identified via a unique ID, usually provided in form of a URI, and should have a clear definition of their meaning.

    * > Semantic resource: A collection of Semantic concepts and potential relationships between them, formalized as controlled vocabulary, thesaurus or ontology.

    * > Semantic repository: Online repository for uploading, discovering and retrieving semantic resources.



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


##########################

Created by Doron Goldfarb, contact: doron.goldfarb@umweltbundesamt.at

(c) 2018, Environment Agency Austria


This work was funded by the European Union via the EUDAT2020 project under grant agreement n.654065
