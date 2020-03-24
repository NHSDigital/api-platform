import requests

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

    def list_keystores(self, environment):
        return requests.get(
            f'https://api.enterprise.apigee.com/v1/organizations/{self.apigee_org}/environments/{environment}/keystores',
            headers=self._auth_headers
        ).json()

    def get_keystore(self, environment, keystore_name):
        return requests.get(f'https://api.enterprise.apigee.com/v1/organizations/{self.apigee_org}/environments/{environment}/keystores/{keystore_name}',
            headers=self._auth_headers
        ).json()

    def create_keystore(self, environment, keystore_name):
        '''
        Create a return a keystore.

        Is idempotent, if keystore already exists will just retrieve.
        '''
        if keystore_name in self.list_keystores(environment):
            return self.get_keystore(environment, keystore_name)
        r = requests.post(
            f'https://api.enterprise.apigee.com/v1/organizations/{self.apigee_org}/environments/{environment}/keystores',
            data={'name': keystore_name},
            headers=self._auth_headers)
        r.raise_for_status()
        return r.json()

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