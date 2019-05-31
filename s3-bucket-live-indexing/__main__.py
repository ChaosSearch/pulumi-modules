import cs_iam
from pulumi import Config, export, ResourceOptions
from pulumi_aws import config, iam, sqs, s3

conf = Config()

#
# Configuration Values and Constants
#
bucket_name = conf.require("cs_data_bucket") + config.region
cs_external_id = conf.require("cs_external_id")

#
# Bucket Resources
#
cs_data_bucket = s3.Bucket(
    "cs_data_bucket",
    bucket=bucket_name,
    acl="private",
    force_destroy=False,
    tags={"Name": bucket_name},
)

#
# SQS Resources
#
cs_s3_bucket_sqs = sqs.Queue(
    "cs_s3_bucket_sqs",
    name=f"s3-sqs-{bucket_name}",
    max_message_size=2048,
    message_retention_seconds=86400,
    visibility_timeout_seconds=480,
    tags={"Bucket": bucket_name},
)

cs_data_bucket_notification = s3.BucketNotification(
    "cs_data_bucket_notification",
    bucket=cs_data_bucket.id,
    queues=[{"queue_arn": cs_s3_bucket_sqs.arn, "events": ["s3:ObjectCreated:*"]}],
    __opts__=ResourceOptions(parent=cs_data_bucket),
)

#
# IAM Resources
#
cs_logging_server_side_role = iam.Role(
    "cs_logging_server_side_role",
    name="cs_logging_server_side_role",
    assume_role_policy=cs_iam.get_cs_assume_role_policy(cs_external_id),
)

cs_logging_server_side_role_policy = iam.Policy(
    "cs_logging_server_side_role_policy",
    name="cs_logging_server_side_role_policy",
    policy=cs_iam.get_server_side_role_policy(cs_data_bucket.arn, cs_external_id),
    __opts__=ResourceOptions(parent=cs_logging_server_side_role),
)

cs_logging_server_side_role_policy_attach = iam.RolePolicyAttachment(
    "cs_logging_server_side_role_policy_attach",
    __name__="cs_logging_server_side_role_policy_attach",
    role=cs_logging_server_side_role.name,
    policy_arn=cs_logging_server_side_role_policy.arn,
    __opts__=ResourceOptions(parent=cs_logging_server_side_role_policy),
)

cs_s3_bucket_sqs_policy = sqs.QueuePolicy(
    "cs_s3_bucket_sqs_policy",
    __name__="cs_s3_bucket_sqs_policy",
    queue_url=cs_s3_bucket_sqs.id,
    policy=cs_iam.get_bucket_sqs_policy(
        cs_s3_bucket_sqs.arn, cs_data_bucket.arn, cs_logging_server_side_role.arn
    ),
    __opts__=ResourceOptions(parent=cs_s3_bucket_sqs),
)

#
# Exports
#
export("cs_data_bucket_bucket", cs_data_bucket.id)
export("cs_logging_serverside_role", cs_logging_server_side_role.arn)
export("sqs_live_logging_arn", cs_s3_bucket_sqs.arn)
