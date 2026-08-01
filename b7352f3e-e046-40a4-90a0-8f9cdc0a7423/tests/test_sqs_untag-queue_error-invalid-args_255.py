def test_untag_queue_rejects_unknown_attribute_definitions(cli, sqs, tmp_path):
    suffix = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )[-40:]
    queue_name = f"untag-invalid-args-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    sqs.rpc(
        "TagQueue",
        {
            "QueueUrl": queue_url,
            "Tags": {
                "remove-me": "original-value",
                "keep-me": "preserved-value",
            },
        },
    )

    result = cli(
        "sqs",
        "untag-queue",
        "--queue-url",
        queue_url,
        "--tag-keys",
        '["remove-me"]',
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags == {
        "remove-me": "original-value",
        "keep-me": "preserved-value",
    }