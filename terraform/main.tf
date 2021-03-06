provider "apigee" {
  org          = var.apigee_organization
  access_token = var.apigee_token
}

terraform {
  backend "azurerm" {}

  required_providers {
    apigee = "~> 0.0"
    archive = "~> 1.3"
  }
}


resource "apigee_target_server" "ig3" {
  count   = length(regexall("sandbox", var.apigee_environment)) > 0 ? 0 : 1
  name    = "ig3"
  host    = var.ig3_url
  env     = var.apigee_environment
  enabled = true
  port    = 443

  ssl_info {
    ssl_enabled              = true
    client_auth_enabled      = true
    key_store                = "ref://backends-keystore"
    key_alias                = "ig3"
    ignore_validation_errors = false
    ciphers                  = []
    protocols                = []
  }
}


resource "apigee_target_server" "identity-server" {
  name    = "identity-server"
  host    = var.identity_url
  env     = var.apigee_environment
  enabled = true
  port    = 443

  ssl_info {
    ssl_enabled              = true
    client_auth_enabled      = false
    ignore_validation_errors = false
    ciphers                  = []
    protocols                = []
  }
}


# For environments except production
# Create, for *internal testing purposes only*:
#  * Internal (hidden) API Product allowing access to everything in the environment
#  * A developer Application subscribed to this product
# Both named `internal-testing-<environment>`

resource "apigee_product" "internal_testing" {
  count   = length(regexall("prod", var.apigee_environment)) > 0 ? 0 : 1
  name = "internal-testing-${var.apigee_environment}"
  display_name = "internal-testing (${var.apigee_environment})"
  description = "For internal testing purposes only. Customers should NOT be subscribed to this product."
  approval_type = "manual"
  api_resources = ["/", "/**", "/*/"]     # Allows access to everything...
  environments = [var.apigee_environment] # ...in this environment

  quota = 60000 # 1000ps
  quota_interval = 1
  quota_time_unit = "minute"

  attributes = {
    access = "internal",
    ratelimit = "1000ps" # Allow up to 1000ps
  }
}

resource "apigee_developer" "internal_testing" {
  count   = length(regexall("prod", var.apigee_environment)) > 0 ? 0 : 1
  email = "apm-testing-${var.apigee_environment}@nhs.net"
  first_name = "Testing"
  last_name = "User"
  user_name = "apm-testing-${var.apigee_environment}"

  attributes = {
    Notes = "Internal testing use ${var.apigee_environment} environment"
  }
}

resource "apigee_developer_app" "internal_testing" {
  count   = length(regexall("prod", var.apigee_environment)) > 0 ? 0 : 1
  name = "internal-testing-${var.apigee_environment}"
  developer_email = length(apigee_developer.internal_testing) > 0 ? apigee_developer.internal_testing[count.index].email : ""
  api_products = [length(apigee_product.internal_testing) > 0 ? apigee_product.internal_testing[count.index].name : "."]
  callback_url = "https://nhsd-apim-testing-${var.apigee_environment}.herokuapp.com/callback"
}
