import time
import BaseHTTPServer
from urlparse import urlparse, parse_qs
from keyterm_extractor import getKeyTerms
from entity_extractor import entityExtractor
import requests
import socket
from pymongo import MongoClient

HOST_NAME = '192.168.56.101' 
PORT_NUMBER = 8000 
client = MongoClient("localhost", 27017)
db = client.Hindu
coll = db.api_key
countries = db.countries

class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(s):
        """Respond to a GET request."""
	q = parse_qs(urlparse(s.path).query)
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
	flag0 = False
	flag1 = False
	flag2 = False
        try:
                api_key = q["api_key"][0]
		if authenticate(api_key):
        		flag0 = True
		else:
			output = {"status":400, "message":"authentication failed"}
			s.wfile.write(str(output))
			return
        except KeyError:
                output= {"status":400, "message":"api_key missing"}
                s.wfile.write(str(output))
		return
	try:
		text = q["text"][0]
		flag1 = True
	except KeyError:
		output= {"status":400, "message":"text field missing"}
		s.wfile.write(str(output))
	try:
		loc = q["country"][0]
		flag2 = True
	except KeyError:
		pass

	
	
	if flag1 and flag0:
		print text
		get_params = "\""+text+"\"&fl=article_title%2C+article_url&wt=json"
		if flag2:
			print "Location Set!"
			ip = get_ip(loc)
			print ip
			machine_status = check_status(ip, 8983)
			print machine_status
			authenticate(api_key)
			if machine_status:
				url = "http://"+ip+":8983/solr/collection1/select?q="+get_params
			else:
				url = "http://192.168.56.101:8983/solr/collection1/select?q="+get_params
		else:
			url = "http://192.168.56.101:8983/solr/collection1/select?q="+get_params
		print url
		r = requests.get(url, stream=True)
		print r.text
        	s.wfile.write(r.text.encode('utf-8'))


def get_ip(loc):
	print loc
	resp = countries.find_one({"country":loc})
	continent = resp["continent"]
	if continent == "Asia":
		ip = "192.168.1.120"
		print ip
		return ip
	if continent == "Africa":
		ip = "192.168.56.101"
		print ip
		return ip
	else:
		ip = "192.168.1.87"
		print ip
		return ip


def check_status(ip, port):
	serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		serv.connect((ip, port))
		serv.close()
		return True
	except socket.error as e:
		print e
		serv.close()
		return False

def authenticate(key):
	print key
	resp = coll.find_one({"key":key})
	if resp == None:
		return False
	else:
		count = int(resp["count"])
		quota = int(resp["quota"])
		if count < quota:
			count = count+1
			coll.update_one({"key":key}, {"$set":{"count":count}})
			return True
		else:
			return False

if __name__ == '__main__':
    server = BaseHTTPServer.HTTPServer
    httpd = server((HOST_NAME, PORT_NUMBER), HttpHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
