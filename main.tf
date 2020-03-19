variable "org" {}
variable "env" {}
variable "user" {}
variable "password" {}
variable "proxy_type" { default = "live" }
variable "ig3_url" { default = "" }
variable "identity_url" { default = "" }


provider "apigee" {
  org = var.org
  user = var.user
  password = var.password
}


resource "apigee_target_server" "ig3" {
  count = var.proxy_type == "live" ? 1 : 0

  name = "ig3"
  host = var.ig3_url
  env = var.env
  enabled = true
  port = 443

  ssl_info {
    ssl_enabled = true
    client_auth_enabled = true
    key_store = "${var.env}-keystore"
    key_alias = "api.service.nhs.uk"
    ignore_validation_errors = false
    ciphers = []
    protocols = []
  }
}


resource "apigee_target_server" "identity-server" {
  count = var.proxy_type == "live" ? 1 : 0

  name = "identity-server"
  host = var.identity_url
  env = var.env
  enabled = true
  port = 443

  ssl_info {
    ssl_enabled = true
    client_auth_enabled = false
    ignore_validation_errors = false
    ciphers = []
    protocols = []
  }
}


module "personal-demographics-service" {
  source = "./modules/service"

  name = "personal-demographics"
  path = "personal-demographics"
  env = var.env
  proxy_type = var.proxy_type
}

