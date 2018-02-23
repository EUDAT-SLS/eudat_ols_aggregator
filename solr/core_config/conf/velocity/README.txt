
This readme and the files in this directory are derived from the Solr 5.5.3 Techproducts example

Doron Goldfarb, Environment Agency Austria, 2018
firstname.lastname[at]umweltbundesamt.at

----------------------------------------------------------------------------------

Introduction
------------
Solr Search Velocity Templates

A quick demo of using Solr using http://wiki.apache.org/solr/VelocityResponseWriter

It's called "browse" because you can click around with your mouse
without needing to type any search terms.  And of course it
also works as a standard search app as well.

Velocity Info
-------------
Java-based template language.

It's nice in this context because change to the templates
are immediately visible in browser on the next visit.

Links:
	http://velocity.apache.org
	http://wiki.apache.org/velocity/
	http://velocity.apache.org/engine/releases/velocity-1.7/user-guide.html


File List
---------

System and Misc:
  VM_global_library.vm    - Macros used other templates,
                            exact filename is important for Velocity to see it
  error.vm                - shows errors, if any
  debug.vm                - includes toggle links for "explain" and "all fields"
                            activated by debug link in footer.vm
  README.txt              - this file

Overall Page Composition:
  browse.vm               - Main entry point into templates
  layout.vm               - overall HTML page layout
  head.vm                 - elements in the <head> section of the HTML document
  header.vm               - top section of page visible to users
  footer.vm               - bottom section of page visible to users,
                            includes debug and help links
  main.css                - CSS style for overall pages
                            see also jquery.autocomplete.css

Query Form and Options:
  query_form.vm           - renders query form
  query_group.vm          - group by fields

Spelling Suggestions:
  suggest.vm              - dynamic spelling suggestions
                            as you type in the search form
  jquery.autocomplete.js  - supporting files for dynamic suggestions
  jquery.autocomplete.css - Most CSS is defined in main.css


Search Results, General:
  (see also browse.vm)
  tabs.vm                 - provides navigation to advanced search options
  pagination_top.vm       - paging and staticis at top of results
  pagination_bottom.vm    - paging and staticis at bottom of results
  results_list.vm	  - render result list, decides which template to use (Single or grouped)
  single_doc.vm           - called for each matching doc,
  hit_grouped.vm          - display results grouped by field values

Search Results, Facets & Clusters:
  facets.vm               - calls the left and right facet templates
  facet_fields[L|R].vm    - display facets based on field values
                            e.g.: fields specified by &facet.field=
