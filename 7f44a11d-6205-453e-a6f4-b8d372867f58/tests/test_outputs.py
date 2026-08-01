"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

import json
import uuid

import pytest


def _qname():
    return "test-queue-" + uuid.uuid4().hex[:10]


def test_create_list_get_url_roundtrip(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    assert r.returncode == 0
    assert r.stderr == ""
    out = json.loads(r.stdout)
    queue_url = out["QueueUrl"]
    assert name in queue_url

    r_list = cli("sqs", "list-queues")
    assert r_list.returncode == 0
    urls = json.loads(r_list.stdout).get("QueueUrls", [])
    assert queue_url in urls

    r_geturl = cli("sqs", "get-queue-url", "--queue-name", name)
    assert r_geturl.returncode == 0
    assert json.loads(r_geturl.stdout)["QueueUrl"] == queue_url


def test_send_receive_delete_message_roundtrip(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    queue_url = json.loads(r.stdout)["QueueUrl"]

    body = "hello-world-" + uuid.uuid4().hex
    r_send = cli("sqs", "send-message", "--queue-url", queue_url, "--message-body", body)
    assert r_send.returncode == 0
    send_out = json.loads(r_send.stdout)
    assert "MessageId" in send_out

    r_recv = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--wait-time-seconds", "5",
        "--max-number-of-messages", "1",
    )
    assert r_recv.returncode == 0
    recv_out = json.loads(r_recv.stdout)
    messages = recv_out.get("Messages", [])
    assert len(messages) == 1
    msg = messages[0]
    assert msg["Body"] == body
    receipt_handle = msg["ReceiptHandle"]

    r_del = cli("sqs", "delete-message", "--queue-url", queue_url, "--receipt-handle", receipt_handle)
    assert r_del.returncode == 0
    assert r_del.stderr == ""
    del_out = json.loads(r_del.stdout)
    assert isinstance(del_out, dict)


def test_delete_queue_removes_from_list_and_breaks_get_url(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    queue_url = json.loads(r.stdout)["QueueUrl"]

    r_del = cli("sqs", "delete-queue", "--queue-url", queue_url)
    assert r_del.returncode == 0
    del_out = json.loads(r_del.stdout)
    assert isinstance(del_out, dict)

    r_list = cli("sqs", "list-queues")
    urls = json.loads(r_list.stdout).get("QueueUrls", [])
    assert queue_url not in urls

    r_geturl = cli("sqs", "get-queue-url", "--queue-name", name)
    assert r_geturl.returncode != 0
    assert r_geturl.stdout == ""
    assert r_geturl.stderr.strip() != ""


def test_unknown_flag_rejected_before_network(cli):
    r = cli("sqs", "create-queue", "--queue-name", _qname(), "--totally-bogus-flag", "x")
    assert r.returncode != 0
    assert r.stdout == ""
    assert r.stderr.strip() != ""
    assert "\n" not in r.stderr.strip("\n")


def test_missing_required_flag_rejected(cli):
    r = cli("sqs", "create-queue")
    assert r.returncode != 0
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_get_queue_attributes_values_are_strings(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    queue_url = json.loads(r.stdout)["QueueUrl"]

    r_attrs = cli(
        "sqs", "get-queue-attributes",
        "--queue-url", queue_url,
        "--attribute-names", "All",
    )
    assert r_attrs.returncode == 0
    attrs = json.loads(r_attrs.stdout).get("Attributes", {})
    for v in attrs.values():
        assert isinstance(v, str)


def test_malformed_json_flag_is_usage_error_not_crash(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    queue_url = json.loads(r.stdout)["QueueUrl"]

    r_bad = cli(
        "sqs", "send-message",
        "--queue-url", queue_url,
        "--message-body", "hi",
        "--message-attributes", "{not-valid-json",
    )
    assert r_bad.returncode != 0
    assert r_bad.stdout == ""
    assert r_bad.stderr.strip() != ""
    assert "Traceback" not in r_bad.stderr


def test_operation_on_nonexistent_queue_errors_cleanly(cli):
    r = cli(
        "sqs", "get-queue-attributes",
        "--queue-url", "http://sqs:9324/000000000000/does-not-exist-queue",
        "--attribute-names", "All",
    )
    assert r.returncode != 0
    assert r.stdout == ""
    assert r.stderr.strip() != ""
    assert "Traceback" not in r.stderr


def test_extra_positional_argument_rejected(cli):
    r = cli("sqs", "list-queues", "unexpected-positional-arg")
    assert r.returncode != 0
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_success_never_writes_to_stderr(cli):
    r = cli("sqs", "list-queues")
    assert r.returncode == 0
    assert r.stderr == ""
    json.loads(r.stdout)


def test_stale_queue_url_after_delete_yields_error(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    queue_url = json.loads(r.stdout)["QueueUrl"]

    r_del = cli("sqs", "delete-queue", "--queue-url", queue_url)
    assert r_del.returncode == 0

    r_send = cli("sqs", "send-message", "--queue-url", queue_url, "--message-body", "ghost")
    assert r_send.returncode != 0
    assert r_send.stdout == ""
    assert r_send.stderr.strip() != ""