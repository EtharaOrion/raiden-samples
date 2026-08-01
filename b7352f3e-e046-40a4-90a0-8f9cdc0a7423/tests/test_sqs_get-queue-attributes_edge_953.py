def test_get_queue_attributes_reports_service_defaults(cli, sqs):
    import json
    import re
    import uuid

    qname = "attr-defaults-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    result = cli("sqs", "get-queue-attributes", "--queue-url", url,
                 "--attribute-names", "All")
    assert result.returncode == 0, result.stderr

    attrs = json.loads(result.stdout)["Attributes"]

    assert attrs["VisibilityTimeout"] == "30"
    assert attrs["DelaySeconds"] == "0"
    assert attrs["ReceiveMessageWaitTimeSeconds"] == "0"
    assert attrs["ApproximateNumberOfMessages"] == "0"
    assert attrs["ApproximateNumberOfMessagesNotVisible"] == "0"
    assert attrs["CreatedTimestamp"].isdigit()
    assert re.fullmatch(r"arn:aws:sqs:[a-z0-9-]+:\d{12}:" + re.escape(qname),
                        attrs["QueueArn"])

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
