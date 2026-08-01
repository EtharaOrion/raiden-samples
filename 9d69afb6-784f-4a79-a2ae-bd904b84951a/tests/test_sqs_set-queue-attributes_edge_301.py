def test_set_queue_attributes_edge_delay_seconds_max_roundtrip(cli, sqs):
    import uuid

    qname = "edge-setattr-delay-max-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    before = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": url,
        "AttributeNames": ["DelaySeconds"],
    })["Attributes"]
    assert before.get("DelaySeconds") != "900"

    # 900s is the documented upper bound for the queue DelaySeconds attribute.
    r = cli(
        "sqs", "set-queue-attributes",
        "--queue-url", url,
        "--attributes", '{"DelaySeconds":"900"}',
    )
    assert r.returncode == 0

    after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": url,
        "AttributeNames": ["DelaySeconds"],
    })["Attributes"]
    assert after["DelaySeconds"] == "900"

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
