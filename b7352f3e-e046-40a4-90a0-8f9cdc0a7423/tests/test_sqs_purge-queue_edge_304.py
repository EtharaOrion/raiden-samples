import uuid


def test_purge_queue_edge_on_already_empty_queue_is_success(cli, sqs):
    qname = "edge-purge-empty-" + uuid.uuid4().hex[:16]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    attrs_before = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": url, "AttributeNames": ["ApproximateNumberOfMessages"],
    })["Attributes"]
    assert int(attrs_before["ApproximateNumberOfMessages"]) == 0

    result = cli("sqs", "purge-queue", "--queue-url", url)
    assert result.returncode == 0

    attrs_after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": url, "AttributeNames": ["ApproximateNumberOfMessages"],
    })["Attributes"]
    assert int(attrs_after["ApproximateNumberOfMessages"]) == 0
