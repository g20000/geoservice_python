from cgi import parse_qs, escape
# importing pyspatialite
from pyspatialite import dbapi2 as db
import time
import os

DB_DIR = '/home/user1/game1/db/'
MIN_SIZE_DEFAULT = 1000

def application(environ, start_response):
	status = '200 OK'
	d = parse_qs(environ['QUERY_STRING'])
	data = d['data'][0].split(',')
	print data
	point_lat = float(data[0])
	point_lng = float(data[1])	
	filename = data[2]
	db_file = searchBestDbFile((point_lat,point_lng),filename)
	print 'using db_file='+db_file
	nearest = getNearest((point_lat,point_lng),db_file)	
	response = "".join([str(nearest)])	
	response_headers = [('Content-type', 'text/html'),('Access-Control-Allow-Origin','*'),('Content-Length',str(len(response)))]	
	start_response(status, response_headers)
	return [response]

def getNearest(point,db_file):
	# creating/connecting the db
	#print 'db_file='+db_file	
	conn = db.connect(DB_DIR + db_file)
	# creating a Cursor
	cur = conn.cursor()
	id_point = getNodeId(cur,point)
	sql = 'SELECT AsGeoJSON(geometry) AS geometry FROM roads_nodes WHERE node_id='+str(id_point)+' LIMIT 1'
	rs = cur.execute(sql)	
	for row in rs:
		result = row[0]		
	cur.close()
	conn.close()
	return result

def getNodeId(cur,point):
	#sql = 'select node_id, MIN(Distance(geometry,MakePoint('+str(start[1])+','+str(start[0])+'))) as rast from roads_nodes'
	try:
		sql = 'select node_id, MIN(Pow(('+str(point[1])+'-X(geometry)),2) +Pow(('+str(point[0])+'-Y(geometry)),2)) as rast from roads_nodes where connected=1'
		rs = cur.execute(sql)	
	except:
		print 'Except: field "connected" not present'
		sql = 'select node_id, MIN(Pow(('+str(point[1])+'-X(geometry)),2) +Pow(('+str(point[0])+'-Y(geometry)),2)) as rast from roads_nodes'
		rs = cur.execute(sql)
	node_id = 0
	for row in rs:
		node_id = row[0]
	return node_id

def searchBestDbFile(point,db_file):
	global DB_DIR
	db_files = os.listdir(DB_DIR)
	min_size = MIN_SIZE_DEFAULT
	best_file = 'undefined'
	for curr_file in filter( lambda fname: fname.find(db_file) == 0, db_files):
		if isInside(curr_file,point):
			size = getAreaSize(curr_file)
			if size <= min_size:
				min_size = size
				best_file = curr_file
	return best_file



def isInside(filename,point):
	boundary = getBoundaryFromName(filename)
	if isPointInside(boundary, point):
		return True
	return False
	
def isPointInside(b, point):
	if len(b) == 0:
		return True
	if point[0] <= b['top'] and point[0] >= b['bottom'] and point[1] <= b['right'] and point[1] >= b['left']:
		return True
	return False

def getBoundaryFromName(name):
	boundary = {}
	ls1 = name.split('[')
	if len(ls1) < 2:
		return boundary
	ls = ls1[1].split(']')[0].split(',')
	if len(ls) < 4:
		return boundary
	boundary['top'] = float(ls[0])
	boundary['left'] = float(ls[1])
	boundary['bottom'] = float(ls[2])
	boundary['right'] = float(ls[3])
	return boundary
	
def getAreaSize(filename):
	boundary = getBoundaryFromName(filename)
	if len(boundary) == 0:
		return MIN_SIZE_DEFAULT
	size = boundary['top'] - boundary['bottom']
	return size