variable "apigee_organization" {
  type = string
  description = "Apigee Org to deploy to."
}

variable "apigee_environment" {
  type = string
  description = "Apigee Env to deploy to."
}

variable "apigee_token" {
  type = string
  description = "Apigee OAuth Access Token."
}

variable "ig3_url" {
  type = string
  description = "URL of spine ig3 for this env."
  default = ""
}

variable "identity_url" {
  type = string
  description = "URL of NHSD ID service for this env."
  default = ""
}

