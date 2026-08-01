def test_list_queue_tags_requires_queue_url(cli, sqs, tmp_path):
    suffix = "".join(c if c.isalnum() else "-" for c in tmp_path.name)[-40:]
    queue_name = f"list-queue-tags-invalid-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": {"purpose": "sentinel"}})

    result = cli("sqs", "list-queue-tags")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert any(url.endswith("/" + queue_name) for url in queues)

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags == {"purpose": "sentinel"}