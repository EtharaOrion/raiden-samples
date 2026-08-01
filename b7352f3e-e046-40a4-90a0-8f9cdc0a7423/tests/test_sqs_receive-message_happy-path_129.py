def test_receive_message_returns_seeded_message_and_hides_it(cli, sqs, tmp_path):
    import json
    import uuid

    queue_name = "receive-happy-" + uuid.uuid4().hex
    queue_url = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {
                "ReceiveMessageWaitTimeSeconds": "2",
                "VisibilityTimeout": "30",
            },
        },
    )["QueueUrl"]

    body = "seeded message body"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})

    before = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessages"]},
    )
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "1"

    result = cli("sqs", "receive-message", "--queue-url", queue_url)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert len(output["Messages"]) == 1
    message = output["Messages"][0]
    assert message["MessageId"] == sent["MessageId"]
    assert message["Body"] == body
    assert message["MD5OfBody"] == sent["MD5OfMessageBody"]
    assert message["ReceiptHandle"]

    subsequent = sqs.rpc(
        "ReceiveMessage",
        {"QueueUrl": queue_url, "WaitTimeSeconds": 1},
    )
    assert not subsequent.get("Messages")