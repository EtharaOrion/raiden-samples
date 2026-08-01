import json
import uuid


def test_list_queue_tags_returns_previously_set_tags(cli, sqs):
    qname = "lqt-happy-" + uuid.uuid4().hex[:16]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]
    assert url.endswith("/" + qname)

    expected = {"env": "prod", "owner": "sqs-team"}
    sqs.rpc("TagQueue", {"QueueUrl": url, "Tags": expected})

    result = cli("sqs", "list-queue-tags", "--queue-url", url)
    assert result.returncode == 0

    parsed = json.loads(result.stdout) if result.stdout.strip() else {}
    tags = parsed.get("Tags") or {}
    for k, v in expected.items():
        assert tags.get(k) == v
