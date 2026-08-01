import json

def test_send_message_delivers_to_queue(cli, sqs):
    queue_name = "test-send-message-happy-q"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello world happy path"
    result = cli("sqs", "send-message", "--queue-url", queue_url, "--message-body", body)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "MessageId" in out and out["MessageId"]

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) == 1

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})