import json
import os
json_path = 'settings.json'


if os.path.exists(json_path) == False:
  os.write(json_path, '{ "prefix": "@-@", "allowed": [] }')

with open(json_path) as user_file:
  options_str = user_file.read()



class SettingsObj:
    allowed = ["test"]
    prefix = "@-@"
    def __init__(self, allowed, prefix):
        self.allowed = allowed
        self.prefix = prefix

data_from_json = json.loads(options_str)

if isinstance(data_from_json["allowed"], list) and isinstance(data_from_json["prefix"],str):
    options = SettingsObj(data_from_json["allowed"], data_from_json["prefix"])
else:
   print("error in settings.json")
   exit()





