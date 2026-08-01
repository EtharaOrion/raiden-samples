"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

import base64
import json
import time
import uuid

import pytest


def _uniq(prefix="tstream"):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _run_ok(cli, *args):
    r = cli(*args)
    assert r.returncode == 0, f"expected success, got rc={r.returncode} stderr={r.stderr!r}"
    assert r.stderr == "" or r.stderr is None or r.stderr.strip() == "", (
        f"stderr must be empty on success, got {r.stderr!r}"
    )
    assert r.stdout.strip() != "", "stdout must contain JSON on success"
    doc = json.loads(r.stdout)
    return doc


def _run_fail(cli, *args):
    r = cli(*args)
    assert r.returncode != 0, "expected non-zero exit code on failure"
    assert r.returncode in (1, 252, 254, 255), f"exit code {r.returncode} not in allowed set"
    assert r.stdout.strip() == "", f"stdout must be empty on failure, got {r.stdout!r}"
    assert r.stderr.strip() != "", "stderr must contain an error line on failure"
    assert "Traceback" not in r.stderr, "no python traceback should leak to stderr"
    return r


def _wait_active(cli, stream_name, attempts=100, delay=0.2):
    for _ in range(attempts):
        r = cli("kinesis", "describe-stream-summary", "--stream-name", stream_name)
        if r.returncode == 0:
            try:
                doc = json.loads(r.stdout)
                status = doc.get("StreamDescriptionSummary", {}).get("StreamStatus")
                if status == "ACTIVE":
                    return doc
            except Exception:
                pass
        time.sleep(delay)
    pytest.fail(f"stream {stream_name} never became ACTIVE")


@pytest.fixture
def stream(cli):
    name = _uniq()
    _run_ok(cli, "kinesis", "create-stream", "--stream-name", name, "--shard-count", "1")
    _wait_active(cli, name)
    yield name
    cli("kinesis", "delete-stream", "--stream-name", name)


def test_create_then_list_streams_consistency(cli, stream):
    doc = _run_ok(cli, "kinesis", "list-streams")
    assert "StreamNames" in doc
    assert stream in doc["StreamNames"]


def test_create_then_describe_stream_consistency(cli, stream):
    doc = _run_ok(cli, "kinesis", "describe-stream", "--stream-name", stream)
    desc = doc.get("StreamDescription", doc)
    assert desc.get("StreamName") == stream


def test_duplicate_create_stream_is_resource_in_use(cli, stream):
    r = _run_fail(cli, "kinesis", "create-stream", "--stream-name", stream, "--shard-count", "1")
    assert r.returncode == 254 or r.returncode == 1
    assert "ResourceInUse" in r.stderr or "InUse" in r.stderr


def test_describe_nonexistent_stream_is_resource_not_found(cli):
    name = _uniq("ghost")
    r = _run_fail(cli, "kinesis", "describe-stream-summary", "--stream-name", name)
    assert "ResourceNotFound" in r.stderr or "NotFound" in r.stderr


def test_unknown_flag_is_usage_error(cli):
    r = _run_fail(cli, "kinesis", "list-streams", "--totally-not-a-real-flag", "value")
    assert r.returncode == 252


def test_missing_required_flag_is_usage_error(cli):
    # create-stream requires --stream-name
    r = _run_fail(cli, "kinesis", "create-stream", "--shard-count", "1")
    assert r.returncode == 252


def test_non_integer_where_int_required_is_usage_error(cli, stream):
    r = _run_fail(cli, "kinesis", "get-records", "--shard-iterator", "abc", "--limit", "notanint")
    assert r.returncode == 252


def test_put_record_roundtrip_via_shard_iterator(cli, stream):
    data = base64.b64encode(b"hello-world-payload").decode()
    partition_key = "pk-123"
    put_doc = _run_ok(
        cli, "kinesis", "put-record",
        "--stream-name", stream,
        "--data", data,
        "--partition-key", partition_key,
    )
    assert "ShardId" in put_doc
    shard_id = put_doc["ShardId"]

    it_doc = _run_ok(
        cli, "kinesis", "get-shard-iterator",
        "--stream-name", stream,
        "--shard-id", shard_id,
        "--shard-iterator-type", "TRIM_HORIZON",
    )
    shard_iterator = it_doc["ShardIterator"]

    records_doc = _run_ok(cli, "kinesis", "get-records", "--shard-iterator", shard_iterator)
    records = records_doc.get("Records", [])
    assert len(records) >= 1
    found = [r for r in records if r.get("PartitionKey") == partition_key]
    assert found, "put record's partition key not found on read-back"
    returned_data = found[0]["Data"]
    # decoded bytes must match, regardless of whether backend re-encodes
    decoded = base64.b64decode(returned_data)
    assert decoded == b"hello-world-payload"


def test_add_and_remove_tags_visible_in_list_tags(cli, stream):
    _run_ok(cli, "kinesis", "add-tags-to-stream", "--stream-name", stream, "--tags", "env=test,owner=qa")
    doc = _run_ok(cli, "kinesis", "list-tags-for-stream", "--stream-name", stream)
    tags = {t["Key"]: t["Value"] for t in doc.get("Tags", [])}
    assert tags.get("env") == "test"
    assert tags.get("owner") == "qa"

    _run_ok(cli, "kinesis", "remove-tags-from-stream", "--stream-name", stream, "--tag-keys", '["env"]')
    doc2 = _run_ok(cli, "kinesis", "list-tags-for-stream", "--stream-name", stream)
    tags2 = {t["Key"]: t["Value"] for t in doc2.get("Tags", [])}
    assert "env" not in tags2


def test_retention_change_reflected_in_describe_summary(cli, stream):
    _run_ok(cli, "kinesis", "increase-stream-retention-period", "--stream-name", stream, "--retention-period-hours", "48")
    doc = _run_ok(cli, "kinesis", "describe-stream-summary", "--stream-name", stream)
    summary = doc.get("StreamDescriptionSummary", doc)
    assert summary.get("RetentionPeriodHours") == 48

    _run_ok(cli, "kinesis", "decrease-stream-retention-period", "--stream-name", stream, "--retention-period-hours", "24")
    doc2 = _run_ok(cli, "kinesis", "describe-stream-summary", "--stream-name", stream)
    summary2 = doc2.get("StreamDescriptionSummary", doc2)
    assert summary2.get("RetentionPeriodHours") == 24


def test_delete_stream_then_eventually_not_found(cli):
    name = _uniq("deleteme")
    _run_ok(cli, "kinesis", "create-stream", "--stream-name", name, "--shard-count", "1")
    _wait_active(cli, name)
    _run_ok(cli, "kinesis", "delete-stream", "--stream-name", name)

    saw_not_found = False
    for _ in range(50):
        r = cli("kinesis", "describe-stream", "--stream-name", name)
        if r.returncode != 0:
            saw_not_found = True
            assert r.stdout.strip() == ""
            assert r.stderr.strip() != ""
            break
        time.sleep(0.2)
    assert saw_not_found, "deleted stream never became not-found"


def test_list_shards_on_nonexistent_stream_fails_not_found(cli):
    name = _uniq("noshards")
    r = _run_fail(cli, "kinesis", "list-shards", "--stream-name", name)
    assert "ResourceNotFound" in r.stderr or "NotFound" in r.stderr