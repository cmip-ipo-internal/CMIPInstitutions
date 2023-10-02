import requests,json
import urllib.parse
from collections import OrderedDict

# Strip out strange characters and insert in the desired format
format_name = lambda n : urllib.parse.quote(n)
# formatted_string = lambda string: bytes(string, 'utf-8').decode('unicode_escape')
# Make the API call
template_file = './base_institutions.json'
url = 'https://api.ror.org/organizations/{}'



def getROR(id):
    response = requests.get(url.format(id))
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data,id
    else:
        print(f"Error: {response.status_code} - {response.text}")
        raise ValueError(f'{id} is not a valid ROR')


def extractROR(jsn,id):
    # Extract desired information
    # print(jsn)
    return {
    'name'     : jsn['name'],
    'country'  : jsn['country'],
    'links'    : jsn['links'],
    'addresses': [
        {'lng': address['lng'], 'lat': address['lat'], 'city': address['city']}
        for address in jsn['addresses']
        ],

    'alt_names': {  'acronyms' : '|'.join(jsn['acronyms']),
                    'aliases'  : '|'.join(jsn['aliases']),
                    'labels'   : jsn['labels'],
                    # '|'.join(jsn['labels'])
                    },

    'establish': jsn['established']
    
    }

    


data = json.load(open(template_file ,'r'))

reverse_map = {}

for key,val in data.copy().items():
    if "Group:" not in key:

        # populate the reverse map
        reverse_map[val["CMIP6key"]] = val["CMIP6key"]

        try:
            data[key].update(extractROR(*getROR(key)))
            
            # add the historic keys. 
            data[key]['alt_names']['CMIPkeys'] = {'CMIP6':val['CMIP6key'],'CMIP5':'','CMIP3':''}

            del data[key]['CMIP6key']

        except ValueError:
            print('skipping '+key)



        

# sort but place groups last 
data = OrderedDict(sorted(data.items(),key=lambda kv: kv[0].replace('Group','zzzz')))

# # Print the modified JSON data
print(json.dumps(data,ensure_ascii=False, indent=4))

#  write the institution file
json.dump(data, open('./verbose_institutions.json','w'),ensure_ascii=False, indent=4)

#  write any CMIP6 mapping to do with this
json.dump(reverse_map, open('./cmip6_institution_map.json', 'w'),ensure_ascii=False, indent=4)