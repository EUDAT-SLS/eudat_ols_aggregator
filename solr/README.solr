
#Use solr_writer.py to transfer data from mongodb to solr

* Loading concepts harvested into MongoDB into Solr core

    * The script [solr_writer.py](solr_writer.py) can be used to transfer data from MongoDB to Solr.
 
      Usage (assuming core name "termcollection":

      python solr_writer.py -M mongoConfig.json -c "http://127.0.0.1:8983/solr/termcollection/"

* Solr configuration

    * The subdirectory [core_config](core_config) provides the respective configuration files based on a Solr 5.5.3 installation. The [core_config/conf/schema.xml](solr/core_config/conf/schema.xml) file and the associated stopword lists are modified/reused from the Solr configuration provided by [EBI-OLS](https://github.com/EBISPOT/OLS/tree/master/ols-solr/src/main/solr-5-config/ontology/conf)

    *  The subdirectory [core_config/conf/velocity](core_config/conf/velocity) contains Velocity templates for rendering the faceted view prototype.

* Velocity based faceted search example on https://bsceudatwp8.bsc.es/termbrowser

    The[faceted class search example](https://bsceudatwp8.bsc.es/termbrowser) operates on 13,8M+ classes harvested from EBI-OLS, AgroPortal and BioPortal in early February 2018. Currently, no instance level terms are included.

    The interface provides a query form with an autosuggest feature supporting the search process. The facets repository, resource prefix and obsolete term allow to drill down on the search results. There are two distinct search modes, "single concept" and "grouped". The "Single concepts" search type allows to enter arbitrary search terms and to retrieve a list of all concepts matching by label. The result list shown in Figure 1 presents for each matching concept its label including a clickable link usually leading to the landing page(s) at the repository or the creator of the resource, the URI, prefix of the resource, resource name and repository name. If available, the concept definition/description is provided in addition.

    <p align="center">
    <img src="https://raw.githubusercontent.com/EUDAT-SLS/eudat_ols_aggregator/28a66a91fbadb72324462803f506d212c472a696/images/solr_single_empty.PNG" width="800"/>
    </p>
    <p align="center">
    Figure 1
    </p>

    The "grouped" search feature is selected by switching to the respective tab above the query form. It currently allows to group by concept ID or concept label. A grouping by term ID is shown in Figure 2. Concepts whose labels match the search term are grouped together by their URI, the resulting groups are sorted by number ofappearances one URI has across the different resources in the different repositories. This way, "popular" concepts in terms of their reuse in different ontologies or taxonomies are highlighted. 

   <p align="center">
    <img src="https://github.com/EUDAT-SLS/eudat_ols_aggregator/blob/28a66a91fbadb72324462803f506d212c472a696/images/solr_group_environment_uri.PNG" width="800"/>
    </p>
    <p align="center">
    Figure 2
    </p>

   The second group search function groups by label as shown in Figure 3. In this case, concepts exactly matching labels are grouped together, providing a complementary view to the URI based grouping.

   <p align="center">
    <img src="https://raw.githubusercontent.com/EUDAT-SLS/eudat_ols_aggregator/28a66a91fbadb72324462803f506d212c472a696/images/solr_group_environment_label.PNG" width="800"/>
    </p>
    <p align="center">
    Figure 3 
    </p>



   


