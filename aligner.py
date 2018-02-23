from DataAnalyzer import DataAnalyzer
from MongoConnector import MongoConnector

from pymongo import MongoClient

import sys
import json

mongoData = json.load(open(sys.argv[1], "r"))
client = MongoClient(mongoData["host"], mongoData["port"])

db = client[mongoData["db"]]

databaserec=MongoConnector( {   "classes"       :       db[mongoData["classes"]],
                                "classes_old"   :       db[mongoData["classes_old"]],
                                "instances"     :       db[mongoData["instances"]],
                                "instances_old" :       db[mongoData["instances_old"]] } )


dataAnalyzer=DataAnalyzer(databaserec)

dataAnalyzer.alignResource("envthes")
