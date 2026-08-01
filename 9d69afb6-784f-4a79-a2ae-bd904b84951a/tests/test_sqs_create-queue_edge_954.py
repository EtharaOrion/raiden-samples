def test_create_queue_response_shape_and_resolvability(cli, sqs):
    import json
    import uuid

    qname = "create-shape-" + uuid.uuid4().hex[:12]

    result = cli("sqs", "create-queue", "--queue-name", qname)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert set(out) == {"QueueUrl"}
    url = out["QueueUrl"]
    assert url.endswith("/" + qname)

    resolved = sqs.rpc("GetQueueUrl", {"QueueName": qname})["QueueUrl"]
    assert resolved == url

    attrs = sqs.rpc("GetQueueAttributes",
                    {"QueueUrl": url, "AttributeNames": ["All"]})["Attributes"]
    assert attrs["QueueArn"].endswith(":" + qname)

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
