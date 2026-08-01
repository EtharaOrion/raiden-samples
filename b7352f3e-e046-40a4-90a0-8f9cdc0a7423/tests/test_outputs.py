"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

import json
import time
import pytest


def _parse_json(stdout):
    assert stdout is not None
    data = json.loads(stdout)
    return data


def _create_queue(cli, name, attributes=None):
    args = ["sqs", "create-queue", "--queue-name", name]
    if attributes is not None:
        args += ["--attributes", json.dumps(attributes)]
    r = cli(*args)
    assert r.returncode == 0, f"create-queue failed: {r.stderr!r}"
    body = _parse_json(r.stdout)
    assert "QueueUrl" in body
    return body["QueueUrl"]


def test_create_queue_visible_in_list_and_get_url(cli):
    name = f"test-cq-{int(time.time()*1000)}"
    url = _create_queue(cli, name)

    r_list = cli("sqs", "list-queues")
    assert r_list.returncode == 0
    listed = _parse_json(r_list.stdout)
    urls = listed.get("QueueUrls", [])
    assert url in urls

    r_geturl = cli("sqs", "get-queue-url", "--queue-name", name)
    assert r_geturl.returncode == 0
    got = _parse_json(r_geturl.stdout)
    assert got.get("QueueUrl") == url


def test_send_receive_delete_message_roundtrip(cli):
    name = f"test-srd-{int(time.time()*1000)}"
    url = _create_queue(cli, name)
    body_text = "hello-world-payload-12345"

    r_send = cli("sqs", "send-message", "--queue-url", url, "--message-body", body_text)
    assert r_send.returncode == 0
    send_resp = _parse_json(r_send.stdout)
    assert "MessageId" in send_resp

    # poll receive a few times (eventual consistency tolerated)
    received = None
    for _ in range(20):
        r_recv = cli("sqs", "receive-message", "--queue-url", url)
        assert r_recv.returncode == 0
        resp = _parse_json(r_recv.stdout)
        msgs = resp.get("Messages") or []
        if msgs:
            received = msgs[0]
            break
        time.sleep(0.3)
    assert received is not None, "message never appeared on receive"
    assert received["Body"] == body_text
    handle = received["ReceiptHandle"]
    assert handle

    r_del = cli("sqs", "delete-message", "--queue-url", url, "--receipt-handle", handle)
    assert r_del.returncode == 0
    assert r_del.stderr == ""


def test_delete_message_stale_handle_is_rejected(cli):
    name = f"test-stale-{int(time.time()*1000)}"
    url = _create_queue(cli, name)

    r = cli("sqs", "delete-message", "--queue-url", url,
            "--receipt-handle", "totally-bogus-handle-value")
    assert r.returncode != 0
    assert r.returncode in (0, 1, 252, 254, 255)
    assert r.returncode != 0
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_purge_queue_converges_to_zero(cli):
    name = f"test-purge-{int(time.time()*1000)}"
    url = _create_queue(cli, name)

    for i in range(3):
        r = cli("sqs", "send-message", "--queue-url", url, "--message-body", f"msg-{i}")
        assert r.returncode == 0

    r_purge = cli("sqs", "purge-queue", "--queue-url", url)
    assert r_purge.returncode == 0
    assert r_purge.stderr == ""

    approx = None
    for _ in range(20):
        r_attr = cli("sqs", "get-queue-attributes", "--queue-url", url,
                     "--attribute-names", "ApproximateNumberOfMessages")
        assert r_attr.returncode == 0
        attrs = _parse_json(r_attr.stdout).get("Attributes", {})
        approx = int(attrs.get("ApproximateNumberOfMessages", "1"))
        if approx == 0:
            break
        time.sleep(0.3)
    assert approx == 0


def test_set_queue_attributes_visible_and_numeric_is_string(cli):
    name = f"test-attrs-{int(time.time()*1000)}"
    url = _create_queue(cli, name)

    r_set = cli("sqs", "set-queue-attributes", "--queue-url", url,
                "--attributes", json.dumps({"VisibilityTimeout": "77"}))
    assert r_set.returncode == 0
    assert r_set.stderr == ""

    r_get = cli("sqs", "get-queue-attributes", "--queue-url", url,
                "--attribute-names", "VisibilityTimeout")
    assert r_get.returncode == 0
    attrs = _parse_json(r_get.stdout).get("Attributes", {})
    assert attrs.get("VisibilityTimeout") == "77"
    assert isinstance(attrs.get("VisibilityTimeout"), str)


def test_tag_and_untag_queue_roundtrip(cli):
    name = f"test-tags-{int(time.time()*1000)}"
    url = _create_queue(cli, name)

    r_tag = cli("sqs", "tag-queue", "--queue-url", url,
                "--tags", json.dumps({"env": "test", "owner": "krishna"}))
    assert r_tag.returncode == 0

    r_list = cli("sqs", "list-queue-tags", "--queue-url", url)
    assert r_list.returncode == 0
    tags = _parse_json(r_list.stdout).get("Tags", {})
    assert tags.get("env") == "test"
    assert tags.get("owner") == "krishna"

    r_untag = cli("sqs", "untag-queue", "--queue-url", url, "--tag-keys", "env")
    assert r_untag.returncode == 0

    r_list2 = cli("sqs", "list-queue-tags", "--queue-url", url)
    assert r_list2.returncode == 0
    tags2 = _parse_json(r_list2.stdout).get("Tags", {})
    assert "env" not in tags2
    assert tags2.get("owner") == "krishna"


def test_delete_queue_then_ops_fail(cli):
    name = f"test-delq-{int(time.time()*1000)}"
    url = _create_queue(cli, name)

    r_del = cli("sqs", "delete-queue", "--queue-url", url)
    assert r_del.returncode == 0
    assert r_del.stderr == ""

    r_after = cli("sqs", "get-queue-attributes", "--queue-url", url)
    assert r_after.returncode != 0
    assert r_after.stdout == ""
    assert r_after.stderr.strip() != ""


def test_fifo_queue_requires_message_group_id(cli):
    name = f"test-fifo-{int(time.time()*1000)}.fifo"
    url = _create_queue(cli, name, attributes={"FifoQueue": "true"})

    r_send = cli("sqs", "send-message", "--queue-url", url, "--message-body", "no-group-id")
    assert r_send.returncode != 0
    assert r_send.stdout == ""
    assert r_send.stderr.strip() != ""


def test_recreate_queue_with_different_attributes_fails(cli):
    name = f"test-dup-{int(time.time()*1000)}"
    _create_queue(cli, name, attributes={"VisibilityTimeout": "10"})

    r2 = cli("sqs", "create-queue", "--queue-name", name,
             "--attributes", json.dumps({"VisibilityTimeout": "99"}))
    assert r2.returncode != 0
    assert r2.stdout == ""
    assert r2.stderr.strip() != ""


def test_unknown_flag_is_usage_error(cli):
    name = f"test-badflag-{int(time.time()*1000)}"
    r = cli("sqs", "create-queue", "--queue-name", name, "--totally-bogus-flag", "x")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_missing_required_flag_is_usage_error(cli):
    r = cli("sqs", "create-queue")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_change_message_visibility_valid_handle_succeeds(cli):
    name = f"test-cmv-{int(time.time()*1000)}"
    url = _create_queue(cli, name)
    r_send = cli("sqs", "send-message", "--queue-url", url, "--message-body", "cmv-body")
    assert r_send.returncode == 0

    handle = None
    for _ in range(20):
        r_recv = cli("sqs", "receive-message", "--queue-url", url)
        msgs = _parse_json(r_recv.stdout).get("Messages") or []
        if msgs:
            handle = msgs[0]["ReceiptHandle"]
            break
        time.sleep(0.3)
    assert handle is not None

    r_cmv = cli("sqs", "change-message-visibility", "--queue-url", url,
                "--receipt-handle", handle, "--visibility-timeout", "5")
    assert r_cmv.returncode == 0
    assert r_cmv.stderr == ""