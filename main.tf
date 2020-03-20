variable "org" {}
variable "env" {}
variable "username" {}
variable "password" {}
variable "ig3_url" { default = "" }
variable "identity_url" { default = "" }


provider "apigee" {
  org = var.org
  user = var.username
  password = var.password
}


resource "apigee_target_server" "ig3" {
  count = length(regexall("sandbox", var.env)) > 0 ? 1 : 0

  name = "ig3"
  host = var.ig3_url
  env = var.env
  enabled = true
  port = 443

  ssl_info {
    ssl_enabled = true
    client_auth_enabled = true
    key_store = "keystore"
    key_alias = "ig3"
    ignore_validation_errors = false
    ciphers = []
    protocols = []
  }
}


resource "apigee_target_server" "identity-server" {
  count = length(regexall("sandbox", var.env)) > 0 ? 1 : 0

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
  proxy_type = length(regexall("sandbox", var.env)) > 0 ? "live" : "sandbox"
}
