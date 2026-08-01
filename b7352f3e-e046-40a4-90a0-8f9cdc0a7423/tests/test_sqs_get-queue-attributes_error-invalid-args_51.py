def test_get_queue_attributes_rejects_unknown_flag(cli, sqs, tmp_path):
    suffix = "".join(ch if ch.isalnum() else "-" for ch in tmp_path.name)
    queue_name = ("get-attributes-invalid-args-" + suffix)[:80]

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "47"},
        },
    )
    queue_url = created["QueueUrl"]

    result = cli(
        "sqs",
        "get-queue-attributes",
        "--queue-url",
        queue_url,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert any(url.endswith("/" + queue_name) for url in queues)

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["VisibilityTimeout"],
        },
    )
    assert attributes["Attributes"]["VisibilityTimeout"] == "47"