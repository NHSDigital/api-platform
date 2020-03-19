# api-platform

## Usage
### Env vars
To authenticate, you'll need to provide some credentials.

Your user account will need sufficient access to deploy to the environment you want to deploy to.

#### Authenticating with user and pass
If you want to use user and pass, then you can set the following in your env:
```
APIGEE_USER="my.username1@nhs.net"
APIGEE_PASSWORD="my-very-very-very-very-very-strong-password"
```

#### Authenticating with token
If you need MFA, you should authenticate and get a token using something like this:
```
$ curl -H "Content-Type: application/x-www-form-urlencoded;charset=utf-8" \
    -H "Accept: application/json;charset=utf-8" \
    -H "Authorization: Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0" \
    -X POST https://login.apigee.com/oauth/token \
    -d "username=my.username1@nhs.net&password=my-very-very-very-very-strong-password&grant_type=password&mfa-token=123456"
```
and take the access token from the response.


Instead, you can use the Apigee-supplied [`get_token`](https://docs.apigee.com/api-platform/system-administration/using-gettoken):
```
$ get_token -u my_username1@nhs.net:my-very-strong-password -m 123456
```

### Running locally
To run locally, first, where `env` is the env you want to deploy:
```
$ terraform plan -var-file=environments/{env}.tfvars
```

If that looks reasonable, then:
```
$ terraform apply -var-file=environments/{env}.tfvars
```

#### Caveat
If you update a proxy bundle, the command may fail saying it could not deploy the new proxy because of a revision mismatch.

To fix this, simply apply again:
```
$ terraform apply -var-file=environments/{env}.tfvars
```

## How to add a new environment
1. Create, commit, and merge a new `environments/{env}.tfvars` file
  a. Set `env` to the env you want to deploy to
  b. Set `org` to the org you want to deploy to
  f. Set `ig3_url` to the correct url for the env
  e. Set `identity_url` to the correct url for the env

2. Check the environment has a TLS keystore, if not create one
  a. Name it `keystore`.
  b. Add the ig3 cert for that env. Name it `ig3` and upload the cert.
  
3. Run the pipeline against the branch to deploy.
