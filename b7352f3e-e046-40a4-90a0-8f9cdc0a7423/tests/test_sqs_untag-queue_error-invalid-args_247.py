def test_untag_queue_missing_queue_url_preserves_tags(cli, sqs, tmp_path):
    queue_name = "untag-required-" + tmp_path.name[-40:]
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": {"keep": "value"}})

    result = cli("sqs", "untag-queue", "--tag-keys", '["keep"]')

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--queue-url" in result.stderr
    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags == {"keep": "value"}