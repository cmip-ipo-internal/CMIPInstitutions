'''
A script to populate the institutions json file using the template provided in this repository. 

This script uses the ROR api. 

Author: Daniel Ellis for the CMIP-IPO and WIP 
contact daniel.ellis (at) ext.esa.int

'''


import requests
import json
import urllib.parse
from collections import OrderedDict
from fuzzywuzzy import fuzz

# Function to format name by stripping out strange characters and inserting in the desired format
# format_name = lambda n: urllib.parse.quote(n)r

# Constants
URL_TEMPLATE = 'https://api.ror.org/organizations/{}'
TEMPLATE_FILE = './template_populated.json'
OUTPUT_FILE = '../institutions.json'


REFERENCE  = "./CMIP6_institution_id.json"
check = json.load(open(REFERENCE, 'r')).get('institution_id')
manual = json.load(open('manual_entry.json', 'r'))



fail = []

def get_ror_data(name):
    """Get ROR data for a given institution name."""
    response = requests.get(URL_TEMPLATE.format(name))

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        err = f"Error: {response.status_code} - {response.text}"
        print(err)
        fail.append(err)
        return None

def parse_ror_data(ror_data):
    """Parse ROR data and return relevant information."""
    if ror_data:

        return {
            "indentifiers": {
                'institution_name': ror_data['name'],
                'aliases': ror_data.get('aliases', []),
                'acronyms': ror_data.get('acronyms', []),
                'labels': [i['label'] for i in ror_data.get('lables', [])],
                'ror': ror_data['id'].split('/')[-1],
                'url': ror_data.get('links', []),
                'established': ror_data.get('established'),
                'type': ror_data.get('types', [])[0] if ror_data.get('types') else None,
            },
            "location": {
                'lat': ror_data['addresses'][0].get('lat') if ror_data.get('addresses') else None,
                'lon': ror_data['addresses'][0].get('lng') if ror_data.get('addresses') else None,
                # 'latest_address': ror_data['addresses'][0].get('line') if ror_data.get('addresses') else None,
                'city': ror_data['addresses'][0].get('city') if ror_data.get('addresses') else None,
            #     'country': ror_data['country']['country_name'] if ror_data.get('country') else None
                'country': list(ror_data['country'].values())  if ror_data.get('country') else None
            },
            "consortiums":[]
            
        }
    else:
        return None

def search_ror(query):

    import requests,json
    import urllib.parse

    # Strip out strange characters and insert in the desired format
    format_name = lambda n : urllib.parse.quote(n)
    # Make the API call
    url = 'https://api.ror.org/organizations?affiliation=%{}s'

    response = requests.get(url.format(query))

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if data.get('items'):
            org = data['items'][0].get('organization')
            return data['items'][0]['score'],org['id'].split('/')[-1], org['name']
        else: return None,None,None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None,None,None


def main():
    # Load data from the template file
    data = json.load(open(TEMPLATE_FILE, 'r'))

    # Dictionary to store institutions data
    institutions = {}
    cohorts = {}

    # Iterate through the template data and fetch ROR information
    for key, val in data.items():

        if "+" in key:
            # Split the key by "+"
            # split_values = sorted(key.split("+"))


            # Rename the key as 'Group:' + CMIP6key value
            new_key = val["CMIP6key"]

            # Create a 'groups' object with the split values
            cohorts[new_key] = {"contains": check[new_key] }

        elif 'CMIP6key' in val:

            name = val.get('CMIP6key')
            # print(ror_name,key,val)

            if key in manual:
                ror_data = get_ror_data(manual[key])
            else:
                ror_data = get_ror_data(key)

            

            parsed_data = parse_ror_data(ror_data)

            

            if parsed_data and key not in manual:
                ratio = fuzz.partial_ratio(check[name], parsed_data["indentifiers"]['institution_name'])
                
                threshold = 60
                if ratio > threshold:
                    institutions[name] = parsed_data
                else: 
                    print(ratio,parsed_data["indentifiers"]['institution_name'],'|')
                    print('\t\t',check[name])
                    print('\t\t',parsed_data)
                    institutions[name] = False
            else:
                institutions[name] = False
        else:
            # not sure if this will be true, but just in case
            name = val.get('CMIP6key')
            institutions[name] = None


    missing = []
    for mip in 'input4MIPS obs4MIPS'.split():
        mipdata  = json.load(open(mip+'_institution_id.json', 'r')).get('institution_id')
        for i in mipdata:
            if i not in institutions:
                if i in manual:
                    ror_data = get_ror_data(manual[i])

                    if ror_data:
                        institutions[i] = parse_ror_data(ror_data)
                    else: 
                        cohorts[i] = manual[i]

                else:
                    missing.append([i,mipdata[i]])


    for k,v in institutions.items():
        if not v:
            if k in manual:
                    ror_data = get_ror_data(manual[k])

                    if ror_data:
                        institutions[k] = parse_ror_data(ror_data)
                    else: 
                        cohorts[k] = manual[k]
            else:
                missing.append([k])

    print('\n\n','-'*10)   
    print(missing)   
    for i in missing: 
        ratio,ror, name = search_ror(''.join(i))
        print()
        print(ratio, f'\n"{i[0]}":"{ror}",')
        print(i,'\n',name)

    assert len(missing) == 0 

  

    # Sort the institutions dictionary and print the JSON data
    institutions = OrderedDict(sorted(institutions.items(), key=lambda item: (item[0][0], 'z' + item[0][1:])))
    # print(json.dumps(institutions, indent=4))
    # print(len(institutions), 'entries')

    # Write the JSON data to the output file
    json.dump(institutions, open(OUTPUT_FILE, 'w'), indent=4)
    json.dump(cohorts, open(OUTPUT_FILE.replace('institutions','cohorts'), 'w'), indent=4)

    with open('faillog.txt','w') as f:
        f.write('\n'.join(fail))
        f.write('\n'.join(missing))



if __name__ == "__main__":
    main()
