#!/bin/bash

pip install -r requirements.txt

wget -O model_data.tgz "https://www.dropbox.com/scl/fi/ekib1ax383yzt55eqk55w/model_data.tgz?rlkey=t94ex64xsuyrula37a6vszlzd&st=gjcjfthy&dl=0"

tar xvzf model_data.tgz
