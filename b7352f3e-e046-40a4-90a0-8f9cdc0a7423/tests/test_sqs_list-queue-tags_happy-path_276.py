def test_list_queue_tags_returns_existing_tags(cli, sqs, tmp_path):
    import json

    queue_name = f"list-tags-{abs(hash(str(tmp_path)))}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    expected_tags = {
        "environment": "test",
        "component": "payments",
    }
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": expected_tags})

    result = cli("sqs", "list-queue-tags", "--queue-url", queue_url)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Tags"] == expected_tags

    resulting_state = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert resulting_state["Tags"] == expected_tags