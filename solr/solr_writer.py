import pysolr
import time
import datetime
import sys
import logging
import json

from pymongo import MongoClient
from optparse import OptionParser

def solrWrite(collection, solrstring):
        logging.info("Get SOLR instance")
	solr=None
	try:
        	solr=pysolr.Solr(solrstring, timeout=60)
 	except:
		logging.critical("Cannot access Solr collection " + str(sys.exc_info()[0]))
		exit(1)
	logging.info("Writing SOLR")
	res=None
	try:
        	res=collection.find()
	except:
		logging.critical("Cannot access Mongo collection " + str(sys.exc_info()[0]))
		exit(1)
        logging.info("Got results")
        cnt=0
        step=10000
        out=list()
        start = time.time()
        lap=start
        for line in res:
                out.append(line)
                if cnt > 0 and cnt % step == 0:
			try:
                        	solr.add(out)
			except:
				logging.critical("Error writing record block to Solr. Reason " + \
						str(sys.exc_info()[0]))
				exit(1)
                        now1=time.time()-lap
                        now2=time.time()-start
                        logging.info("Added " + str(step) + " recs in " + str(now1) + \
					", total " + str(cnt) + " in " + str (now2))
                        lap=time.time()
                        out=list()
                cnt+=1
	try:
        	solr.add(out)
	except:
		logging.warning("Error writing record to Solr. Reason " + \
				str(sys.exc_info()[0]) + " Data: " + repr(out))
		pass

#################### MAIN BLOCK #############################

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

parser = OptionParser()

parser.add_option("-M", "--mongodb", dest="mongodb",
                  help="Read MONGO DB config and maintain MONGO connection", metavar="DB")

parser.add_option("-s", "--solr", dest="solrstring",
                  help="Specify Solr connection URL", metavar="solr")

parser.add_option("-t", "--type", dest="type",
                  help="Create index for -t classes or for -t instances ", metavar="classes/instances")

(options, args) = parser.parse_args()

err=False

termcollection=None

if options.mongodb != None:
	mongoData=json.loads(open(options.mongodb).read())
	client = MongoClient(mongoData["host"], mongoData["port"])
	db = client[mongoData["db"]]
	termtype="classes"
	if options.type=="instances":
		termtype="instances"
	termcollection = db[mongoData[termtype]]
else:
	err=True

solrstring=None
if options.solrstring != None:
	solrstring=options.solrstring
else:
	err=True

if err:
	parser.print_help()
	exit(1)
else:
	solrWrite(termcollection, solrstring)
	
	


