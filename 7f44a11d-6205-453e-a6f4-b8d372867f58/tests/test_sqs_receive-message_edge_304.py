def test_receive_message_edge_wait_time_zero_on_empty_queue(cli, sqs):
    import json
    import time
    import uuid

    qname = "edge-recv-wait-zero-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    t0 = time.monotonic()
    r = cli(
        "sqs", "receive-message",
        "--queue-url", url,
        "--wait-time-seconds", "0",
        "--max-number-of-messages", "1",
    )
    elapsed = time.monotonic() - t0
    assert r.returncode == 0
    assert elapsed < 10.0

    parsed = json.loads(r.stdout) if r.stdout.strip() else {}
    assert not (parsed.get("Messages") or [])

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
