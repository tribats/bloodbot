# bloodbot

![Deploy workflow](https://github.com/tribats/bloodbot/workflows/terraform/badge.svg)

This is my personal website that is published by Github actions to AWS on
push to the default branch. The site is served via CloudFront from an S3
origin. All the AWS resources are managed via Terraform.

## Deployment

When there is a push to the default branch, Github actions will do the following:

- Plan and apply any Terraform changes
- Update the Lambda

### Pre-Requisites

- AWS credentials with access to manage all the required resources.
  I am terrible and have a way too permissive user I use for this in an
  otherwise empty account and will hopefully get around to listing the actual
  least-privileged policy required some day.

- Slack webhook URL

### Secrets

IRL the SLACK_WEBHOOK_URL should be pulled from something like SecretsManager
but here it's just injected as an environment variable to the lambda.

| Secret                | Description           | Example                                                          |
| --------------------- | --------------------- | ---------------------------------------------------------------- |
| AWS_ACCESS_KEY_ID     | aws access key ID     | AKIAIOSFODNN7EXAMPLE                                             |
| AWS_SECRET_ACCESS_KEY | aws access key secret | wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY                         |
| SLACK_WEBHOOK_URL     | slack webhook url     | https://hooks.slack.com/services/D34DB33F/R2D2C3P0/H4CktH3Pl4n3T |
