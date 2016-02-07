import pysolr
from pymongo import MongoClient
from keyterm_extractor import getKeyTerms
from entity_extractor import entityExtractor
import sys

client = MongoClient("localhost", 27017)
s = pysolr.Solr('http://localhost:8983/solr/collection1', timeout=10)

db = client.Hindu
coll = db.editions

for doc in coll.find({"date":"06-02-2016"}):
	try:
		date = doc["date"]
		for page in doc['pages']:
			for article in page['articles']:
				article["page"] = page["page_name"]
				article["date"] = date
				article["keyterms"] = getKeyTerms(article['article_text'])
				article["entities"] = entityExtractor(article['article_text'])
				u = article["article_url"]
				temp = u.split("/")
				temp = temp[len(temp)-1]
				temp = temp.split(".")[0][-7:]
				article["id"] = temp 
				s.add([article])
	except:
		print "Failed!"
