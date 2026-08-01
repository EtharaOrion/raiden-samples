import base64
import json
import time


def _wait_active(cli, stream_name, tries=60):
    """Poll describe-stream through the CLI until the stream reports ACTIVE."""
    for _ in range(tries):
        d = cli("kinesis", "describe-stream", "--stream-name", stream_name)
        if d.returncode == 0:
            sd = json.loads(d.stdout)["StreamDescription"]
            if sd["StreamStatus"] == "ACTIVE" and sd.get("Shards"):
                return sd
        time.sleep(0.2)
    raise AssertionError("stream %s never became ACTIVE" % stream_name)


def test_workflow_put_record_read_back(cli, kinesis, tmp_path):
    """create-stream -> put-record -> get-shard-iterator -> get-records, all via CLI."""
    stream = "wf-putget-" + str(int(time.time() * 1000))

    c = cli("kinesis", "create-stream", "--stream-name", stream, "--shard-count", "1")
    assert c.returncode == 0, c.stderr

    sd = _wait_active(cli, stream)
    shard_id = sd["Shards"][0]["ShardId"]

    payload = base64.b64encode(b"wf-roundtrip-payload").decode()
    partition_key = "wf-pk-1"
    p = cli("kinesis", "put-record", "--stream-name", stream,
            "--data", payload, "--partition-key", partition_key)
    assert p.returncode == 0, p.stderr
    put = json.loads(p.stdout)
    assert "ShardId" in put and "SequenceNumber" in put

    it = cli("kinesis", "get-shard-iterator", "--stream-name", stream,
             "--shard-id", shard_id, "--shard-iterator-type", "TRIM_HORIZON")
    assert it.returncode == 0, it.stderr
    shard_iterator = json.loads(it.stdout)["ShardIterator"]

    found = False
    for _ in range(10):
        g = cli("kinesis", "get-records", "--shard-iterator", shard_iterator)
        assert g.returncode == 0, g.stderr
        out = json.loads(g.stdout)
        for rec in out.get("Records", []):
            if rec.get("PartitionKey") == partition_key and rec.get("Data") == payload:
                found = True
                break
        if found:
            break
        shard_iterator = out.get("NextShardIterator")
        if not shard_iterator:
            break
        time.sleep(0.2)

    assert found, "record written via CLI was not read back via CLI"

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass
