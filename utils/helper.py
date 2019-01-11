import numpy as np
import json
import os.path
import requests as rq
import cv2


# Getting MAC Address
def get_mac():
    a = nf.interfaces()
    b = nf.ifaddresses(a[1])[nf.AF_LINK]
    mac_add = b[0]['addr'].upper()
    return mac_add
# Get Cam Info from server


def get_data(mac_add, url, path):
    request = rq.get(url+'/'+path,
                     headers={'Content-type': 'application/json', 'Authorization': mac_add})
    value = request.text

    Data = json.loads(value)
    Data = Data['EmoData']
    info = dict()
    if len(Data) == 0:
        info['cam_url'] = 0
    else:
        Data = Data[0]
        info['mac_address'] = Data['mac_address']
        info['ip_address'] = Data['ip_address']
        info['cam_url'] = Data['cam_url']
        info['adv_title'] = Data['adv_title']
    return(info)
# Read Server info


def read_json(filename):
    with open(filename) as json_data:
        d = json.load(json_data)
    return d
# Capture the Face and Store in images folder


def captureFace(face, faceid):
    cv2.imwrite('./aceva/emotion/images/'+faceid+'.png', face)
    return True
# # Post Data to Server
# def post (url,path,auth,data):
#     urlfull = url+'/'+path
#     headers = {'Content-type': 'application/json','Authorization':auth}
#     r = rq.post(urlfull, data=json.dumps(data), headers=headers)
#     return (r.text, r.status_code)
#


def post(url, path, auth, data):
    urlfull = 'http://'+url+'/'+path
    headers = {'Content-type': 'application/json', 'Authorization': auth}
    r = rq.post(urlfull, data=json.dumps(data), headers=headers)
    return (r.text, r.status_code)
