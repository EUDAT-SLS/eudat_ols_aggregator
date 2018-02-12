# EUDAT Semantic Lookup Service Harvester

Harvesting of Semantic Repositories

## Files:

### Configuration:

[(repoConfig_noapikey.json](repoConfig_noapikey.json) - Example configuration for three Semantic Repositories EBI-OLS, Bioportal and Agroportal. For the latter two, API keys must be obtained for each and inserted into the respective fields in the json file.

[mongoConfig.json](mongoConfig.json) - Specify host and port of used MongoDB instance, collections for repositories, classes and instances

[mandatory.json](mandatory.json) - Specify which fields must be present for a term to be stored into the DB.

### Code

[DataContainer.py](DataContainer.py) - Class for handling Semantic Repository descriptions as shown in [(repoConfig_noapikey.json](repoConfig_noapikey.json).

[MongoConnector.py](MongoConnector.py) - Class for storing terms harvested via [DataContainer.py](DataContainer.py) to MongoDB instance specified via [mongoConfig.json](mongoConfig.json). An instance of this class must be passed to the root DataContainer instance and is reused there.

[retrieve.py](retrieve.py) - Script for harvesting terms from repositories using the above configuration files and [DataContainer.py](DataContainer.py)


##########################

(c) 2018, Doron Goldfarb, Environment Agency Austria, contact: doron.goldfarb@umweltbundesamt.at

This work was funded by the European Union via the EUDAT2020 project under grant agreement n.654065
