variable "org" {}
variable "env" {}


provider "apigee" {
  org = "${var.org}"
  user = "${var.user}"
  password = "${var.password}"
}


module "personal-demographics-service" {
  source = "./service.tf"

  name = "personal-demographics"
  path = "personal-demographics"
}
