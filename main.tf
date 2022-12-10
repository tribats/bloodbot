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

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = var.state_bucket
  acl    = "private"

  versioning = {
    enabled = true
  }
}

module "eventbridge" {
  source = "terraform-aws-modules/eventbridge/aws"

  create_bus = false

  rules = {
    cron = {
      description         = "Trigger for a Lambda"
      schedule_expression = "rate(1 hour)"
    }
  }

  targets = {
    cron = [
      {
        name = "lambda-cron"
        arn  = "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.lambda_function_name}"
      }
    ]
  }
}

module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "4.2.2"

  function_name = var.lambda_function_name
  description   = "Slack bot to notify when inventory changes"
  handler       = "app.main"
  runtime       = "python3.8"
  publish       = true

  source_path = "${path.module}/src"

  environment_variables = {
    SLACK_WEBHOOK_URL = var.slack_webhook_url
    STATE_BUCKET      = var.state_bucket
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
      resources = ["${module.s3_bucket.s3_bucket_arn}/*"]
    }
  }

  allowed_triggers = {
    cron = {
      principal  = "events.amazonaws.com"
      source_arn = module.eventbridge.eventbridge_rule_arns.cron
    }
  }
}

resource "null_resource" "example" {
  triggers = {
    value = "noop-changed"
  }
}
