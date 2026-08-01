def test_get_queue_attributes_invalid_args(cli, sqs, tmp_path):
    queue_name = "test-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs",
        "get-queue-attributes",
        "--queue-url",
        queue_url,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "rgument" in result.stderr or "Unknown" in result.stderr

    # Queue must still exist and be readable via the valid RPC path
    attrs = sqs.rpc("GetQueueAttributes", {"QueueUrl": queue_url, "AttributeNames": ["All"]})
    assert "Attributes" in attrs
    assert "ApproximateNumberOfMessages" in attrs["Attributes"]

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))