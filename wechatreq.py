from flask import Flask
from flask_restful import Api, Resource, reqparse
import json
import cv2
import codecs, json
import urllib

app = Flask(__name__)
api = Api(app)

location = input("Please the source of the image : ")

name_identifier = location.split("/")

if "www." in location:
    #print("hi")
    url = location
    filename = url.split('/')
    count = len(filename)
    lastname = filename[-count + (count-1)]
    ##print(count)
    ##print(lastname)
    urllib.request.urlretrieve(url,lastname)

    img = cv2.imread(lastname,1)
    img_str = ' '.join(map(str,img.flatten().tolist()))

    users = [{
                        "name" : "image",
                        "image" : img_str
                      }]
else:
    #print("hello")
    url = location

    img = cv2.imread(url,1)
    img_str = ' '.join(map(str,img.flatten().tolist()))

    users = [{
                        "name" : "image",
                        "image" : img_str
                      }]


class User(Resource):
    def get(self, name):
        for user in users:
            if(name == user["name"]):
                return user, 200
        return "User not found", 404


    def post(self, name):
        for user in users:
            if(name == user["name"]):
                return user, 201

    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("image")

        args = parser.parse_args()

        for user in users:
            if(name == user["name"]):
                user["image"] = args["image"]

                return user, 200

        user = {
            "name":name,
            "age":args["image"]
        }
        users.append(user)
        return user, 201

    def delete(self, name):
        global users
        users = [user for user in users if user["name"] != name]
        return "{} is deleted.".format(name),200


api.add_resource(User, "/user/<string:name>")
app.run(debug = True)
