#!/bin/bash
source venv/bin/activate
python3 yolo４.py -m /home/aitclab2011/akari_yolo_inference/model/key_candy.blob -c /home/aitclab2011/akari_yolo_inference/json/key_candy_best.json
