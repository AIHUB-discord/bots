import json
import os
json_path = 'settings.json'


if os.path.exists(json_path) == False:
  os.write(json_path, '{ "allowed": [] }')

with open(json_path) as user_file:
  options_str = user_file.read()



class SettingsObj:
    allowed = ["test"]
    def __init__(self, allowed):
        self.allowed = allowed

data_from_json = json.loads(options_str)

if isinstance(data_from_json["allowed"], list):
    options = SettingsObj(data_from_json["allowed"])
else:
   print("error in settings.json")
   exit()





