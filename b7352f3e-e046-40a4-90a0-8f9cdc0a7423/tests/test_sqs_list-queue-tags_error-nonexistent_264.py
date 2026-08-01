def test_list_queue_tags_nonexistent_queue(cli, sqs, tmp_path):
    token = str(abs(hash(str(tmp_path))))
    control_name = f"control-{token}"
    missing_name = f"missing-{token}"

    control_url = sqs.rpc("CreateQueue", {"QueueName": control_name})["QueueUrl"]
    missing_url = sqs.rpc("CreateQueue", {"QueueName": missing_name})["QueueUrl"]
    sqs.rpc("DeleteQueue", {"QueueUrl": missing_url})

    result = cli("sqs", "list-queue-tags", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "QueueDoesNotExist" in result.stderr
        or "NonExistentQueue" in result.stderr
    )

    queue_urls = sqs.rpc("ListQueues", {"QueueNamePrefix": ""}).get("QueueUrls", [])
    assert any(url.endswith(f"/{control_name}") for url in queue_urls)
    assert not any(url.endswith(f"/{missing_name}") for url in queue_urls)