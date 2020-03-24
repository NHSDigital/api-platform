"""
spec_uploader.py

A tool for uploading apigee specs

Usage:
  spec_uploader.py <apigee_org> <specs_dir> -u <username> -p <password>
  spec_uploader.py (-h | --help)

Options:
  -h --help  Show this screen
  -u         Which username to log in with
  -p         Password for login
"""
import os
from docopt import docopt
from apigee_client import ApigeeClient

def upload_specs(specs_dir, client):
    # Grab a list of local specs
    local_specs = os.listdir(specs_dir)

    # Grab a list of remote specs
    folder = client.list_specs()
    folder_id = folder['id']
    existing_specs = {v['name']: v['id'] for v in folder['contents']}

    # Figure out where the portal is
    portal_id = client.get_portals().json()['data'][0]['id']
    print(f'portal is {portal_id}')
    portal_specs = {i['specId']: i for i in client.get_apidocs(portal_id).json()['data']}
    print(f'grabbed apidocs')

    # Run through the list of local specs -- if it's on the portal, update it;
    # otherwise, add a new one
    for spec in local_specs:
        spec_name = os.path.splitext(spec)[0]

        if spec_name in existing_specs:
            print(f'{spec} exists')
            spec_id = existing_specs[spec_name]
        else:
            print(f'{spec} does not exist, creating')
            response = client.create_spec(spec_name, folder_id)
            spec_id = response.json()['id']

        print(f'{spec} id is {spec_id}')

        with open(os.path.join(specs_dir, spec), 'r') as f:
            response = client.update_spec(spec_id, f.read())
            print(f'{spec} updated')

        print(f'checking if this spec is on the portal')
        if spec_name in portal_specs:
            print(f'{spec} is on the portal, updating')
            apidoc_id = portal_specs[spec_name]['id']
            client.update_spec_snapshot(portal_id, apidoc_id)
        else:
            print(f'{spec} is not on the portal, adding it')
            client.create_portal_api(spec_name, spec_id, portal_id)

    print('done.')


if __name__ == "__main__":
    args = docopt(__doc__)
    client = ApigeeClient(args['<apigee_org>'], args['<username>'], args['<password>'])
    upload_specs(args['<specs_dir>'], client)
