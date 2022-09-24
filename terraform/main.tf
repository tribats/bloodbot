terraform {
  backend "remote" {
    organization = "bluemage"

    workspaces {
      name = "bloodbot"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "ca-central-1"
}

module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = var.state_bucket
  acl    = "private"

  versioning = {
    enabled = true
  }
}

module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "bloodbot"
  description   = "Slack bot to notify when inventory changes"
  handler       = "app.main"
  runtime       = "python3.9"

  source_path = "../src"

  environment_variables = {
    SLACK_WEBHOOK_URL = var.slack_webhook_url
  }

  attach_policy_statements = true
  policy_statements = {
    list_objects = {
      effect    = "Allow",
      actions   = ["s3:ListBucket"],
      resources = [module.s3_bucket.s3_bucket_arn]
    },
    allow_object_actions = {
      effect    = "Allow",
      actions   = ["s3:*Object", "s3:GetObject"],
      resources = ["{module.s3_bucket.s3_bucket_arn}/*"]
    }
  }

  allowed_triggers = {
    OneRule = {
      principal  = "events.amazonaws.com"
      source_arn = "arn:aws:events:ca-central-1:135367859851:rule/RunDaily"
    }
  }
}

resource "null_resource" "example" {
  triggers = {
    value = "noop-changed"
  }
}
