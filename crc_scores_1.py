import json
import falcon
import random
import uuid
import pickle
import os.path
import pprint


empty_reputee_dict = {}  #creating a global dictionary object
print('before', empty_reputee_dict)
pickleDB = 'datafile.pkl'  #for data persistence of dictionary

def create_pickelDB():
    F1 = open(pickleDB, 'wb')
    pickle.dump(empty_reputee_dict, F1) #adding empty dictionary
    F1.close()

def db_check():
    #want to check if the dictionary exists or not, if not then create
    while True:
        print('db_check')
        if os.path.isfile(pickleDB):
            print('yes pickelDB exists, now check for reputee in it')
            break
        else:
            print('there is no pickleDB... I am making one now and will rerun this function')
            create_pickelDB()
db_check()

def update_reputee_dict(posted):
    #this function receives the data posted by the client and parces it
    reputer = posted['reputer']
    reputee = posted['reputee']
    feature = posted['repute']['feature']
    rid = posted['repute']['rid']
    rid_value = posted['repute']['value']
    updating_reputee_dict(reputee, feature, rid, rid_value)

def updating_reputee_dict(a,b,c,d):
    #this function receives the parsed data and updates the dictionary database
    # updating_reputee_dict(reputee, feature, rid, rid_value)
    with open(pickleDB, 'rb') as f:
        print('can you see me?')
        reputee_dict = pickle.load(f)
        # reputee_check(reputee_dict)
        print('reputee_dict before ')
        pprint.pprint(reputee_dict)
    with open(pickleDB, 'wb') as f:
        """The following try/except statements test a) if the reputee
        is in the database, and adds all info if not, b) if the feature
        is in the database for that reputee, and adds all info if not,
        and c) if the rid for that feature and reputee is in the database,
        and adds all info if not."""
        D3, D2 = {}, {}
        try:
            reputee_dict[a]     #if reputee exists, move to next try
        except KeyError:        #if not add all info
            D3[c] = d
            D2[b] = D3
            reputee_dict[a] = D2
        try:
            reputee_dict[a][b]  #if reputee feature exists, move to next try
        except KeyError:        #if not, add all info
            D3[c] = d
            reputee_dict[a][b] = D3
        try:
            reputee_dict[a][b][c]   #if rid exists, then do nothing
        except KeyError:            #if rid does not exist, then add it
            reputee_dict[a][b][c] = d
        pickle.dump(reputee_dict, f)
        print('reputee_dict after ')
        pprint.pprint(reputee_dict)


def json_generator():
    """This function creates a json string in a .json file that, when posted using
    $ http localhost:8000/crc_scores_1 field:=@~/workspace/xt2/xt2/reputedata.json
     allows httpie to use the json string in reputedata.json as the POST material"""

    name_of_reputer = random.choice(['Deen','Andy','James','Loomis'])
    name_of_reputee = random.choice(['Mike','Jacobus','Quinn','Matthew'])
    rid_value = str(uuid.uuid4())
    feature_reach = ['reach']
    feature_clarity = ['clarity']
    r_or_c = feature_reach + feature_clarity
    reach_or_clarity = random.choice(r_or_c)
    zero_to_ten = random.randint(0,10)

    rec = {
        'reputer': name_of_reputer,
        'reputee': name_of_reputee,
        'repute':
            {
            'rid': rid_value,
            'feature': reach_or_clarity,
            'value': zero_to_ten
            }
          }

    json.dump(rec, fp=open('reputedata.json', 'w'), indent=4)
    print('This is the json data just written', open('reputedata.json').read())

data_dict = {"hello client": "This is the new GET; Here is your info"}

class Reputee_Scores(object):

    def on_get(self, req, resp):
        gdoc = data_dict
        # creating a JSON string representation of the gdoc Resource
        # resp.body is a python object that specifies the JSON response to client
        resp.body = json.dumps(gdoc, ensure_ascii=False)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        json_generator()  #reputedata.json is empty on first test run; populate manually
        data_in_field = json.loads(req.stream.read().decode('utf-8'))
        data = data_in_field['field']
        update_reputee_dict(data)
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(data, ensure_ascii=False)
        resp.location = '/crc_scores_1'


F2 = open(pickleDB, 'rb')
E2 = pickle.load(F2)
print('Final databasecheck', E2)
F2.close()


api = falcon.API()
api.add_route('/crc_scores_1', Reputee_Scores())

"""
GET
Terminal 1:
(.venv) Aludas-iMac:workspace aluda$ cd xt2/xt2/
(.venv) Aludas-iMac:xt2 aluda$ gunicorn --reload crc_scores_1:api
Terminal 2:
$ http localhost:8000/crc_scores_1

POST
Terminal 1:
(.venv) Aludas-iMac:workspace aluda$ cd xt2/xt2/
(.venv) Aludas-iMac:xt2 aluda$ gunicorn --reload crc_scores_1:api
Terminal 2:
(POST is implied when data follow URI)

With HTTPie you can autoconvert to json
$ http localhost:8000/crc_scores_1 hello=postingserver

Or you can write your own json with httpie
$ http localhost:8000/crc_scores_1 field:='{"1":"2"}'

In this module, I create a .json file and fill it with json
and drop outer quotes; {"just":"brackets"}
$ http localhost:8000/crc_scores_1 field:=@~/workspace/xt2/xt2/reputedata.json
"""
