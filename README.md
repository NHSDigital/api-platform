# api-platform

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
