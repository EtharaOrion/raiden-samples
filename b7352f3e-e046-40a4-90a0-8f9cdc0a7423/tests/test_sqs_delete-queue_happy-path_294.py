def test_delete_queue_removes_existing_queue(cli, sqs, tmp_path):
    queue_name = "delete-queue-" + str(abs(hash(str(tmp_path))))
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)

    assert result.returncode == 0
    remaining_urls = sqs.rpc(
        "ListQueues", {"QueueNamePrefix": queue_name}
    ).get("QueueUrls", [])
    assert not any(url.endswith("/" + queue_name) for url in remaining_urls)