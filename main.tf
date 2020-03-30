variable "apigee_organization" {}
variable "apigee_environment" {}
variable "apigee_token" {}
variable "ig3_url" { default = "" }
variable "identity_url" { default = "" }


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
  count = length(regexall("sandbox", var.apigee_environment)) > 0 ? 0 : 1

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


module "personal-demographics-service" {
  source = "github.com/NHSDigital/api-platform-service-module"

  name               = "personal-demographics"
  path               = "personal-demographics"
  apigee_environment = var.apigee_environment
  proxy_type         = length(regexall("sandbox", var.apigee_environment)) > 0 ? "sandbox" : "live"
}
