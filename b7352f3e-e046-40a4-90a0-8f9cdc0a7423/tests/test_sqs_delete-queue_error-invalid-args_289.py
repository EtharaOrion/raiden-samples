def test_delete_queue_rejects_invalid_arguments_without_deleting_queue(cli, sqs, tmp_path):
    suffix = "".join(character for character in tmp_path.name if character.isalnum())[-40:]
    queue_name = f"delete-invalid-args-{suffix}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]

    result = cli(
        "sqs",
        "delete-queue",
        "--queue-url",
        queue_url,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    queue_urls = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert any(url.endswith("/" + queue_name) for url in queue_urls)