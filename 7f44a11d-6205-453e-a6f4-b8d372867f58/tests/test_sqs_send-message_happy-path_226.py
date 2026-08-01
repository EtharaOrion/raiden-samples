def test_send_message_happy_path(cli, sqs):
    import json

    queue_name = "test-send-message-happy-path-q"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello world message body 123"

    result = cli(
        "sqs", "send-message",
        "--queue-url", queue_url,
        "--message-body", body,
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert out.get("MessageId")

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) >= 1

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})