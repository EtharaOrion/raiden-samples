def test_purge_queue_edge_on_already_empty_queue(cli, sqs):
    import uuid

    qname = "edge-purge-empty-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    # Purge on a queue that is already empty must succeed.
    r = cli("sqs", "purge-queue", "--queue-url", url)
    assert r.returncode == 0

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) == 0

    # The queue must still be usable afterwards.
    sqs.rpc("SendMessage", {"QueueUrl": url, "MessageBody": "post-purge-empty"})
    attrs2 = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": url,
        "AttributeNames": ["All"],
    })["Attributes"]
    assert (int(attrs2.get("ApproximateNumberOfMessages", "0"))
            + int(attrs2.get("ApproximateNumberOfMessagesDelayed", "0"))
            + int(attrs2.get("ApproximateNumberOfMessagesNotVisible", "0"))) >= 1

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
