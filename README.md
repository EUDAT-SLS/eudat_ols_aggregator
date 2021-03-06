# EUDAT Semantic Lookup Service Harvester


This is a prototypical implementation for a service which harvests information about semantic concepts from semantic resources hosted via dedicated repositories. The main purpose for this service within EUDAT is to support interdisciplinary annotation of data by providing controlled terminology to services such as [EUDAT B2Note](https://github.com/EUDAT-B2NOTE/b2note). For a broader description of the approach see [(Goldfarb & Le Franc, 2017)](http://ceur-ws.org/Vol-1933/paper-7.pdf)

The service basically consists of a script which consumes a configuration file describing the locations and APIs of Semantic repositories (Currently: BioPortal, AgroPortal and EBI-OLS) in order to harvest the information about the semantic resources and concepts hosted there. The resulting data is written into a database (Currently: MongoDB) in unified form, mainly consisting of concept ID, preferred label, synonyms, description as well as resource and repository level information.

The content of the db can subsequently be fed into a Solr index which can be used for various lookup services. A faceted search preview for the results of the harvesting of BioPortal, AgroPortal and EBI-OLS can be explored at https://bsceudatwp8.bsc.es/termbrowser

# Quickstart

* **Invocation**

    The following call starts the harvesting process for EBI-OLS, BioPortal and AgroPortal using the configuration file examples provided in this repository. Please note that [repoConfig_noapikey.json](repoConfig_noapikey.json) must be edited regarding the API keys for Bio- and AgroPortal, thus called repoConfig.json here.

    **./retrieve.py -c repoConfig.json -m mandatory.json -M mongoConfig.json**  

    One full harvesting run for the three repositories downloads information for approximately 15M concepts, this can take 48+ hours, so be patient.

    For testing purposes, a number of options exist to limit the harvesting to specific repositories and/or resources,

    **./retrieve.py --help**

    lists the available program arguments.

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

      the [solr directory](solr) contains various items for creating the Solr index. See [solr/README.md](solr/README.md) for further information.

* **Requirements:**

    * **MongoDB:**

      A running MongoDB installation is required, its adress etc. should be configured in [mongoConfig.json](mongoConfig.json). A dedicated database with four collections must be explicitely created. There are two pairs of collections, one for classes, one for instances. Each pair consists of one collection for "current" classes/instances and one for "old" ones. In each harvesting run, classes/instances with changed data are moved to the "old" collection and overwritten in the "current" one. The default configuration in [mongoConfig.json](mongoConfig.json) assumes the following: A database EUDAT_OLS with collections for classes: "termcollection" and "oldtermcollection" and instances: "instancecollection" and "oldinstancecollection"

    * **Repository configuration:**

      The list of configured repositories can be passed as file such as in [repoConfig_noapikey.json](repoConfig_noapikey.json) or stored in the MongoDB in a dedicated collection, which can also be specified via [mongoConfig.json](mongoConfig.json)

    * **System configuration:**

      It is highly advisable to have sufficient RAM available on the machine running the harvester, EBI-OLS, Bioportal and Agroportal together yield about 15M classes/instances.


# Documentation

This section describes the structure of the harvester in more detail.

* **Definitions**


    * **Semantic concept:** 

        Classes, individuals, concepts or terms serving as building blocks for knowledge organization systems such as ontologies, thesauri or controlled vocabularies. A main requirement is that these entities are identified via a unique ID, usually provided in form of a URI, and should have a clear definition of their meaning.

    * **Semantic resource:** 

        A collection of Semantic concepts and potential relationships between them, formalized as controlled vocabulary, thesaurus or ontology.

    * **Semantic repository:**

        Online repository for uploading, discovering and retrieving semantic resources.

* **Implementation**

    The design principle for the harvester was to create a flexible way to harvest concept and resource level data from different Semantic repositories. Table 1 lists the information which shall be harvested for each concept, representing a data tuple describing the repository, the resource and the concept.

    | Level | Field |
    |:-----:|:-----:|
    |Concept|ID (URI)|
    ||Preferred Label|
    ||Description|
    ||Synonyms|
    |Resource|Acronym|
    ||ID (URI)|
    ||Name|
    ||Version Date|
    ||Version Info|
    |Repository|Name|
    Table 1


    None of the encountered repositories provide means to access information from such different levels via one single API call, but require a two-step procedure instead. For each repository, one call retrieves a list of its hosted resources, which is subsequently iterated in order to issue per-resource second level calls for retrieving the concepts present there, usually again returned as lists. The overall sequence for accessing different repositories is sketched in Figure 1. 

    <!-- <figure style="display: block; margin-left: auto; margin-right: auto"> -->
    <p align="center">
    <img src="https://raw.githubusercontent.com/EUDAT-SLS/eudat_ols_aggregator/adea9dc6f063b09d6ce4ff3cf1ed45e6bebaac2e/images/basic_workflow.PNG" width="500"/>
    </p>
    <p align="center">
    Figure 1
    </p>

    Since the different repositories provide different APIs to be used in such harvesting sequences, there are two main approaches to represent them programatically. One would be to create a plugin architecture with distinct harvesting workflows implemented as individual plugins. The other would be to create code that is flexible enough to be adapted to the individual repository APIs via configuration files. This implementation follows the latter approach, since the basic harvesting sequence was to be found very similar across repositories. As Figure 1 moreover suggests, there is an apparent self-similarity between the iterations at the different levels of each harvesting sequence, motivating to find a mechanism which can be recursively applied to these different levels, driven via a similarly recursive configuration file. 

    Figure 2 shows a diagram of the *DataContainer* class used here to implement such a mechanism ([DataContainer.py](DataContainer.py)). It is based on the assumption that in each level, 

	1. One or more fields to be harvested (cf Table1) are provided via an explicitly given REST API call issued via URL and returned as JSON
	2. The results of the API call are returned as list, i.e. issuing the given REST API call for the "resources" level will return a list of resources and descriptive metadata about them.
	3. The location of the list within the JSON file and the individual items within this list, bearing the desired field data can be described via JSONpath
	4. The returned list of items is iterated and for each item, the configured field data extracted. As long as the lowest level (usually: concept level) is not reached, each list item spawns a new class instantiation configured to harvest lower level information.

    <p align="center">
    <img src="https://raw.githubusercontent.com/EUDAT-SLS/eudat_ols_aggregator/adea9dc6f063b09d6ce4ff3cf1ed45e6bebaac2e/images/DataContainer.PNG" width="300"/>
    </p>
    <p align="center">
    Figure 2
    </p>

    Figure 3 shows the recursive instantiation of *DataContainer* objects as progressing through the different harvesting steps. 

    <p align="center">
    <img align="middle" src="https://raw.githubusercontent.com/EUDAT-SLS/eudat_ols_aggregator/adea9dc6f063b09d6ce4ff3cf1ed45e6bebaac2e/images/DataContainer_invocation.PNG"/>
    </p>
    <p align="center">
    Figure 3
    </p>

    The instantiation and processing of the *DataContainer* objects at the different levels are governed via dedicated configuration files. As indicated above, the current implementation assumes JSON to be the format of the API call results, using JSONpath to locate and extract field information accordingly. The configuration files are therefore also represented via JSON. Figure 4 shows an example for a configuration for the EBI-OLS repository. Each level is represented via distinct blocks:

	| Element | Purpose |
	|:-------:|:-------:|
	|Level    | Information about the current level |
	|URL	  | The URL for the REST API call|
	|next	  | JSONpath to "next page" URL for paginated call results|
	|list	  | JSONpath to location of item list within call results|  
	|fields	  | Dictionary of fields to be extracted for each item in result list (key: Field name, value: JSONpath location/Static value)|
	|resources| Recursive description of lower level configuration|

   Field information is provided via path/type tuples, enabling to specify if the field data is to be extracted via JSONpath (path = JSONpath, type ="literal/list") or provided as static string (path = static string, type ="static")

   Information provided via the URL field has a special feature, where parts of the provided URL can be marked as tokens which shall be substituted with information extracted for higher level fields. This is indicated in Figure 4 via the red arrows, showing how the part of the URL needed to specify the specific resource for which lower level information is about to be harvested is provided via the respective <ontoprefix> token referring to the field already harvested at resource level. 

    <p align="center">
    <img src="https://raw.githubusercontent.com/EUDAT-SLS/eudat_ols_aggregator/adea9dc6f063b09d6ce4ff3cf1ed45e6bebaac2e/images/exampleconfig.PNG" width="800"/>
    </p>
    <p align="center">
    Figure 4
    </p>

* **References:**

    (Goldfarb & Le Franc, 2017) 
    D. Goldfarb and Y. Le Franc. Enhancing the Discoverability and Interoperability of Multi-Disciplinary Semantic Repositories. In: A. Algergawy, N. Karam, F. Klan, C. Jonquet: Proc. of the 2nd International Workshop on Semantics for Biodiversity co-located with 16th International Semantic Web Conference (ISWC 2017), Vienna, Austria, October 22nd, 2017. CEUR Workshop Proceedings 1933


##########################

Created by Doron Goldfarb, contact: doron.goldfarb@umweltbundesamt.at

(c) 2018, Environment Agency Austria


This work was funded by the European Union via the EUDAT2020 project under grant agreement n.654065
