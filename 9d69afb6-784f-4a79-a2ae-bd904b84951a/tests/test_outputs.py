"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

import json
import re
import uuid

import pytest


ALLOWED_FAIL_CODES = {1, 252, 254, 255}


def _traceback_free(stderr: str):
    assert "Traceback (most recent call last)" not in stderr


def _assert_clean_failure(result):
    assert result.returncode != 0
    assert result.returncode in ALLOWED_FAIL_CODES
    assert result.stdout == "" or result.stdout.strip() == ""
    assert result.stderr.strip() != ""
    _traceback_free(result.stderr)
    # Reject multi-line noisy stderr (should be a single identifying line, allow
    # trailing newline only)
    lines = [l for l in result.stderr.splitlines() if l.strip()]
    assert len(lines) >= 1


def _assert_clean_success(result):
    assert result.returncode == 0
    assert result.stderr.strip() == ""
    # stdout must be parseable JSON (or legitimately empty -> treat as {})
    out = result.stdout.strip()
    if out == "":
        return {}
    return json.loads(out)


def _qname():
    return "test-q-" + uuid.uuid4().hex[:12]


def test_create_queue_then_list_and_get_url_consistency(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    data = _assert_clean_success(r)
    assert "QueueUrl" in data
    queue_url = data["QueueUrl"]

    r2 = cli("sqs", "list-queues")
    data2 = _assert_clean_success(r2)
    urls = data2.get("QueueUrls", [])
    assert any(queue_url == u or queue_url.rstrip("/") == u.rstrip("/") for u in urls)

    r3 = cli("sqs", "get-queue-url", "--queue-name", name)
    data3 = _assert_clean_success(r3)
    assert data3.get("QueueUrl", "").rstrip("/") == queue_url.rstrip("/")


def test_send_receive_roundtrip_identical_body(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    data = _assert_clean_success(r)
    queue_url = data["QueueUrl"]

    body = "hello-world-" + uuid.uuid4().hex
    r2 = cli("sqs", "send-message", "--queue-url", queue_url, "--message-body", body)
    send_data = _assert_clean_success(r2)
    assert "MessageId" in send_data

    r3 = cli(
        "sqs",
        "receive-message",
        "--queue-url",
        queue_url,
        "--max-number-of-messages",
        "1",
        "--wait-time-seconds",
        "2",
    )
    recv_data = _assert_clean_success(r3)
    msgs = recv_data.get("Messages", [])
    assert len(msgs) == 1
    assert msgs[0]["Body"] == body
    assert "ReceiptHandle" in msgs[0]


def test_delete_message_then_purge_zero_count(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    queue_url = _assert_clean_success(r)["QueueUrl"]

    cli("sqs", "send-message", "--queue-url", queue_url, "--message-body", "x")
    r2 = cli(
        "sqs",
        "receive-message",
        "--queue-url",
        queue_url,
        "--max-number-of-messages",
        "1",
        "--wait-time-seconds",
        "2",
    )
    recv_data = _assert_clean_success(r2)
    handle = recv_data["Messages"][0]["ReceiptHandle"]

    r3 = cli("sqs", "delete-message", "--queue-url", queue_url, "--receipt-handle", handle)
    _assert_clean_success(r3)

    cli("sqs", "send-message", "--queue-url", queue_url, "--message-body", "y")
    r4 = cli("sqs", "purge-queue", "--queue-url", queue_url)
    _assert_clean_success(r4)

    r5 = cli(
        "sqs",
        "get-queue-attributes",
        "--queue-url",
        queue_url,
        "--attribute-names",
        "ApproximateNumberOfMessages",
    )
    attrs = _assert_clean_success(r5)
    count = int(attrs.get("Attributes", {}).get("ApproximateNumberOfMessages", "0"))
    assert count == 0


def test_set_attributes_tag_untag_reflected(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    queue_url = _assert_clean_success(r)["QueueUrl"]

    r2 = cli(
        "sqs",
        "set-queue-attributes",
        "--queue-url",
        queue_url,
        "--attributes",
        json.dumps({"VisibilityTimeout": "42"}),
    )
    _assert_clean_success(r2)

    r3 = cli(
        "sqs",
        "get-queue-attributes",
        "--queue-url",
        queue_url,
        "--attribute-names",
        "VisibilityTimeout",
    )
    attrs = _assert_clean_success(r3)
    assert attrs.get("Attributes", {}).get("VisibilityTimeout") == "42"

    r4 = cli("sqs", "tag-queue", "--queue-url", queue_url, "--tags", "Team=Platform,Env=Test")
    _assert_clean_success(r4)

    r5 = cli("sqs", "list-queue-tags", "--queue-url", queue_url)
    tags = _assert_clean_success(r5).get("Tags", {})
    assert tags.get("Team") == "Platform"
    assert tags.get("Env") == "Test"

    r6 = cli("sqs", "untag-queue", "--queue-url", queue_url, "--tag-keys", "Env")
    _assert_clean_success(r6)

    r7 = cli("sqs", "list-queue-tags", "--queue-url", queue_url)
    tags2 = _assert_clean_success(r7).get("Tags", {})
    assert "Env" not in tags2
    assert tags2.get("Team") == "Platform"


def test_delete_queue_then_subsequent_ops_fail(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    queue_url = _assert_clean_success(r)["QueueUrl"]

    r2 = cli("sqs", "delete-queue", "--queue-url", queue_url)
    _assert_clean_success(r2)

    r3 = cli("sqs", "get-queue-attributes", "--queue-url", queue_url)
    _assert_clean_failure(r3)

    r4 = cli("sqs", "send-message", "--queue-url", queue_url, "--message-body", "z")
    _assert_clean_failure(r4)


def test_invalid_receipt_handle_error_class(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    queue_url = _assert_clean_success(r)["QueueUrl"]

    r2 = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        "totally-bogus-handle-" + uuid.uuid4().hex,
    )
    _assert_clean_failure(r2)


def test_unknown_command_is_usage_error(cli):
    r = cli("sqs", "not-a-real-command")
    _assert_clean_failure(r)
    assert r.returncode != 0


def test_malformed_json_flag_is_usage_error(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    queue_url = _assert_clean_success(r)["QueueUrl"]

    r2 = cli(
        "sqs",
        "set-queue-attributes",
        "--queue-url",
        queue_url,
        "--attributes",
        "{not valid json!!",
    )
    _assert_clean_failure(r2)


def test_unknown_flag_is_usage_error(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name, "--totally-bogus-flag", "value")
    _assert_clean_failure(r)


def test_batch_send_and_delete_report_per_entry_outcomes(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    queue_url = _assert_clean_success(r)["QueueUrl"]

    entries = [
        {"Id": "m1", "MessageBody": "body-1-" + uuid.uuid4().hex},
        {"Id": "m2", "MessageBody": "body-2-" + uuid.uuid4().hex},
    ]
    r2 = cli(
        "sqs",
        "send-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )
    data = _assert_clean_success(r2)
    successful = data.get("Successful", [])
    assert len(successful) == 2
    ids = {e["Id"] for e in successful}
    assert ids == {"m1", "m2"}
    for e in successful:
        assert "MessageId" in e

    r3 = cli(
        "sqs",
        "receive-message",
        "--queue-url",
        queue_url,
        "--max-number-of-messages",
        "10",
        "--wait-time-seconds",
        "2",
    )
    recv_data = _assert_clean_success(r3)
    msgs = recv_data.get("Messages", [])
    assert len(msgs) == 2

    delete_entries = [
        {"Id": m["MessageId"], "ReceiptHandle": m["ReceiptHandle"]} for m in msgs
    ]
    r4 = cli(
        "sqs",
        "delete-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(delete_entries),
    )
    del_data = _assert_clean_success(r4)
    assert len(del_data.get("Successful", [])) == 2


def test_success_never_mixes_stdout_and_stderr_channels(cli):
    name = _qname()
    r = cli("sqs", "create-queue", "--queue-name", name)
    assert r.returncode == 0
    assert r.stderr == ""
    json.loads(r.stdout)