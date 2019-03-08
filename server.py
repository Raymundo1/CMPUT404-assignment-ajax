#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# Modified work Copyright 2019 Xinlei Chen
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request, redirect, jsonify, make_response
import json
from hashlib import md5
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        
    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data

    def clear(self):
        self.space = dict()

    def get(self, entity):
        return self.space.get(entity,dict())
    
    def world(self):
        return self.space

    def get_etag(self):
        return md5(json.dumps(self.space).encode('utf-8')).hexdigest()

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World() 
etag =  myWorld.get_etag()

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    return redirect('/static/index.html', code=301)

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    global etag
    '''update the entities via this interface'''
    # update the whole bucket of this entity
    myWorld.set(entity, flask_post_json())
    etag = myWorld.get_etag()
    response = make_response(jsonify(myWorld.get(entity)), 200)
    return response

@app.route("/world", methods=['POST','GET'])    
def world():
    '''you should probably return the world here'''
    # https://stackoverflow.com/questions/45412228/flask-sending-data-and-status-code-through-a-response-object
    # author: Nabin
    
    if ("If-None-Match" in request.headers):
        if(request.headers['If-None-Match'] != etag):
            response = make_response(jsonify(myWorld.world()), 200)
            response.headers['ETag'] = etag
        else:
            response = make_response("", 200)
            response.headers['ETag'] = "false"
    else:
        response = make_response(jsonify(myWorld.world()), 200)
    
    return response

@app.route("/entity/<entity>")    
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    response = make_response(jsonify(myWorld.get(entity)), 200)
    return response

@app.route("/clear", methods=['POST','GET'])
def clear():
    global etag
    '''Clear the world out!'''
    myWorld.clear()
    response = make_response(jsonify(myWorld.world()), 200)
    etag = myWorld.get_etag()
    return response

if __name__ == "__main__":
    app.run()
