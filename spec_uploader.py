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
import json
import requests
from docopt import docopt


class ApigeeClient:
    def __init__(self, apigee_org, username, password):
        self.apigee_org = apigee_org
        self.access_token = self._get_access_token(username, password)

    def list_specs(self):
        return requests.get(
            f'https://apigee.com/dapi/api/organizations/{self.apigee_org}/specs/folder/home',
            headers=self._auth_headers
        ).json()

    def create_spec(self, name, folder):
        return requests.post(
            f'https://apigee.com/dapi/api/organizations/{self.apigee_org}/specs/doc',
            json={
                "folder": folder,
                "name": name,
                "kind": "Doc"
            },
            headers=self._auth_headers
        )

    def update_spec(self, spec_id, content):
        return requests.put(
            f'https://apigee.com/dapi/api/organizations/{self.apigee_org}/specs/doc/{spec_id}/content',
            headers=dict(**{'Content-Type': 'text/plain'}, **self._auth_headers),
            data=content.encode('utf-8')
        )

    def get_portals(self):
        return requests.get(
            f'https://apigee.com/portals/api/sites?orgname={self.apigee_org}',
            headers=self._auth_headers
        )

    def get_apidocs(self, portal_id):
        return requests.get(
            f'https://apigee.com/portals/api/sites/{portal_id}/apidocs',
            headers=self._auth_headers
        )


    def create_portal_api(self, spec_name, spec_id, portal_id):
        return requests.post(
            f'https://apigee.com/portals/api/sites/{portal_id}/apidocs',
            json={
                "anonAllowed": True,
                "description": "",
                "edgeAPIProductName": spec_name,
                "requireCallbackUrl": False,
                "specContent": spec_id,
                "specId": spec_name,
                "title": spec_name,
                "visibility": True
            },
            headers=self._auth_headers
        )

    def get_apidoc(self, portal_id, apidoc_id):
        return requests.get(
            f'https://apigee.com/portals/api/sites/{portal_id}/apidocs/{apidoc_id}',
            headers=self._auth_headers
        )

    def update_spec_snapshot(self, portal_id, apidoc_id):
        apidoc = self.get_apidoc(portal_id, apidoc_id).json()['data']

        requests.put(
            f'https://apigee.com/portals/api/sites/{portal_id}/apidocs/{apidoc_id}',
            json={
                "anonAllowed": True,
                "description": apidoc['description'],
                "specId": apidoc['specId'],
                "visibility": True
            },
            headers=self._auth_headers
        )

        requests.put(
            f'https://apigee.com/portals/api/sites/{portal_id}/apidocs/{apidoc_id}/snapshot',
            headers=self._auth_headers
        )

    @property
    def _auth_headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}'
        }

    def _get_access_token(self, username, password):
        response = requests.post(
            'https://login.apigee.com/oauth/token',
            data={
                'username': username,
                'password': password,
                'grant_type': 'password'
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0'
            }
        )

        return response.json()['access_token']

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
