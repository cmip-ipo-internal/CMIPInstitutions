import requests,json
import urllib.parse
from collections import OrderedDict

# Strip out strange characters and insert in the desired format
format_name = lambda n : urllib.parse.quote(n)
# Make the API call

template_file = './template_populated.json'
url = 'https://api.ror.org/organizations?affiliation=%{}s'
debug = False


data = json.load(open(template_file ,'r'))

for key,val in data.copy().items():
    if "+" in key:
        # Split the key by "+"
        split_values = sorted(key.split("+"))

        for id in split_values:
            if id not in data:
                data[id] = {'CMIP6key': None}

        
        # Rename the key as 'Group:' + CMIP6key value
        new_key = "Group:" + val["CMIP6key"]

        # Create a 'groups' object with the split values
        data[new_key] = {"contains": split_values, 'CMIP6key': val.get('CMIP6key')}
        
        # Remove the old key    
        del data[key]

        

# sort but place groups last 
data = OrderedDict(sorted(data.items(),key=lambda kv: kv[0].replace('Group','zzzz')))

# Print the modified JSON data
print(json.dumps(data, indent=4))
print(len(data), 'entries')

json.dump(data, open('./base_institutions.json','w'), indent=4)



