def test_purge_queue_removes_messages(cli, sqs):
    queue_name = "test-purge-queue-happy"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    for i in range(3):
        sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": f"msg-{i}"})

    attrs_before = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs_before["Attributes"]["ApproximateNumberOfMessages"]) > 0

    result = cli("sqs", "purge-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    attrs_after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs_after["Attributes"]["ApproximateNumberOfMessages"]) == 0

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})