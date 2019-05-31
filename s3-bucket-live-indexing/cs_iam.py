import json
from pulumi import Output


def get_cs_assume_role_policy(cs_external_id):
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Effect": "Allow",
                },
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"AWS": "arn:aws:iam::515570774723:root"},
                    "Effect": "Allow",
                    "Condition": {"StringEquals": {"sts:ExternalId": cs_external_id}},
                },
            ],
        }
    )


def get_bucket_sqs_policy(sqs_arn, bucket_arn, role_arn):
    arns = Output.all(sqs_arn, bucket_arn, role_arn)
    return arns.apply(
        lambda vals: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "sqs:SendMessage",
                        "Resource": vals[0],
                        "Condition": {"ArnEquals": {"aws:SourceArn": vals[1]}},
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": [vals[2]]},
                        "Action": "sqs:*",
                        "Resource": vals[0],
                    },
                ],
            }
        )
    )


def get_cs_assume_role_policy(cs_external_id):
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Effect": "Allow",
                },
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"AWS": "arn:aws:iam::515570774723:root"},
                    "Effect": "Allow",
                    "Condition": {"StringEquals": {"sts:ExternalId": cs_external_id}},
                },
            ],
        }
    )


def get_server_side_role_policy(bucket_arn, cs_external_id):
    arns = Output.all(bucket_arn)
    return arns.apply(
        lambda vals: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:Get*", "s3:List*", "s3:PutObjectTagging"],
                        "Resource": [vals[0], f"{vals[0]}/*"],
                    },
                    {
                        "Effect": "Allow",
                        "Action": ["s3:ListAllMyBuckets"],
                        "Resource": "*",
                    },
                    {
                        "Effect": "Allow",
                        "Action": "*",
                        "Resource": [f"arn:aws:s3:::cs-{cs_external_id}"],
                    },
                    {
                        "Effect": "Allow",
                        "Action": "*",
                        "Resource": [f"arn:aws:s3:::cs-{cs_external_id}/*"],
                    },
                ],
            }
        )
    )
