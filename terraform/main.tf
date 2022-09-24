terraform {
  backend "remote" {
    organization = "bluemage"

    workspaces {
      name = "bloodbot"
    }
  }
}

resource "null_resource" "example" {
  triggers = {
    value = "noop-changed"
  }
}
