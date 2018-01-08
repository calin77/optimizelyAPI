import requests
import pandas as pd
import json as json
import re

from pymongo import MongoClient
client = MongoClient()
db = client.tests
coll = db.allexp


i = 1
newtotalpages = 1

def apicall(page):
    myUrl = 'http://api.optimizely.com/v2/experiments?project_id=4821381483&per_page=100&page=' + str(page)
    head = {"Authorization":"Bearer 2:x8WZAQOO9yBx9FlVEBDRWrzJmvvGPsFSoaVUSGWoUM5nggaTS8fM"}
    response = requests.get(myUrl, headers=head)
    data = response.json()
    # coll.insert(data)
    checkdata(data)

def expresults(expid):
    print expid
    coll = db[str(expid)]
    query=''
    cursor = coll.find_one({'_id': 'cr001'})
    if cursor != None and cursor['start_time'] and cursor['end_time']:
        query= "?start_time="+str(cursor['start_time'])+"&"+"end_time="+str(cursor['end_time'])
    myUrl = 'https://api.optimizely.com/v2/experiments/' + str(expid) + '/results' + query
    print myUrl
    head = {"Authorization":"Bearer 2:x8WZAQOO9yBx9FlVEBDRWrzJmvvGPsFSoaVUSGWoUM5nggaTS8fM"}
    response = requests.get(myUrl, headers=head)
    if response.status_code == requests.codes.ok:
        data = response.json()
        cursor = coll.find_one({'experiment_id': long(expid), 'start_time': data['start_time'], 'end_time': data['end_time']})
        if cursor == None:
            print 'Update document'
            coll.update({'experiment_id': long(expid)}, data)
        else:
            print 'item exist'
    else :
        print str(expid) + ' no data api'

def checkdata(data):
    for item in data:
        itemdate = pd.to_datetime(item['last_modified'])
        cursor = db.allexp.find_one({'id': long(item['id'])})
        if item['status'] == 'running':
            expresults(item['id'])
        if cursor != None:
            cursordate = pd.to_datetime(cursor['last_modified'])
            if cursordate != itemdate:
                # update document
                coll.update({'id': long(item['id'])}, item)
                print str(item['id']) + ' item updated'
        else:
            print 'Insert new document'
            coll.insert(item)


myUrl = 'http://api.optimizely.com/v2/experiments?project_id=4821381483&per_page=100&page=1'
head = {"Authorization":"Bearer 2:x8WZAQOO9yBx9FlVEBDRWrzJmvvGPsFSoaVUSGWoUM5nggaTS8fM"}
response = requests.get(myUrl, headers=head)
data = response.json()
if data:
    checkdata(data)
    header = response.headers
    mylink =  header['Link']
    print mylink
    parse = mylink.split(',')
    for current in range(len(parse)):
        if (parse[current].find("rel=last")!= -1):
            m = re.search(r'&page=\d', parse[current])
            newtotalpages = int(filter(str.isdigit, m.group(0)))




while i < newtotalpages:
    # call the api next page
    i = i + 1
    print 'call again page ' + str(i)
    apicall(i)
