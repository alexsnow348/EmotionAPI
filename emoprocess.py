#!/home/ace/.virtualenvs/VA/bin/python
"""Emotion Detetion Module.

This module detects the emotion of visitors.

"""

import aceva
import aceva.emotion as EMO
# import threading
import multiprocessing
# from datetime import datetime

source = aceva.read_json('./input.json')
url = source['url']
imgprod = source['imgprod']
vidprod = source['vidprod']
qmsprod = source['qmsprod']
emoprod = source['emo_get']
emoprod_post = source['emo_post']

# mac_add = aceva.get_mac()
mac_add = '94:C6:91:1C:64:DF'
source = aceva.read_json('input.json')
cam_data = aceva.get_data_target(mac_add, url, emoprod)

emoProcess = []

for each in cam_data:
    p_emo = multiprocessing.Process(target=EMO.main.emotionVideo,
                                    args=(mac_add, url, emoprod_post, each,))
    emoProcess.append(p_emo)
    p_emo.start()

for j in range(len(emoProcess)):
    emoProcess[j].join()
