def test_tag_queue_missing_required_tags(cli, sqs, tmp_path):
    queue_name = "tag-queue-invalid-" + str(abs(hash(str(tmp_path))))
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    sqs.rpc("TagQueue", {
        "QueueUrl": queue_url,
        "Tags": {"existing": "unchanged"},
    })

    result = cli("sqs", "tag-queue", "--queue-url", queue_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--tags" in result.stderr

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags == {"existing": "unchanged"}