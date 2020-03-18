variable "org" {}
variable "env" {}

provider "apigee" {
  org = "${var.org}"
  user = "${var.user}"
  password = "${var.password}"
}
