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
  count   = length(regexall("sandbox", var.apigee_environment)) > 0 ? 0 : 1
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
