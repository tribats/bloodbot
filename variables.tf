variable "slack_webhook_url" {
  type      = string
  sensitive = true
}

variable "state_bucket" {
  type = string
}

variable "lambda_function_name" {
  type    = string
  default = "bloodbot"
}
