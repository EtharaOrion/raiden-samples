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


def test_workflow_tag_untag_delete(cli, kinesis, tmp_path):
    """create-stream -> add-tags -> remove-tags -> delete-stream, all through the CLI."""
    stream = "wf-tags-" + str(int(time.time() * 1000))

    c = cli("kinesis", "create-stream", "--stream-name", stream, "--shard-count", "1")
    assert c.returncode == 0, c.stderr
    _wait_active(cli, stream)

    t = cli("kinesis", "add-tags-to-stream", "--stream-name", stream,
            "--tags", '{"env":"wf","team":"data"}')
    assert t.returncode == 0, t.stderr
    tags = {x["Key"]: x["Value"]
            for x in kinesis.rpc("ListTagsForStream", {"StreamName": stream}).get("Tags", [])}
    assert tags.get("env") == "wf"

    rm = cli("kinesis", "remove-tags-from-stream", "--stream-name", stream,
             "--tag-keys", "env")
    assert rm.returncode == 0, rm.stderr
    keys = {x["Key"]
            for x in kinesis.rpc("ListTagsForStream", {"StreamName": stream}).get("Tags", [])}
    assert "env" not in keys

    d = cli("kinesis", "delete-stream", "--stream-name", stream)
    assert d.returncode == 0, d.stderr

    for _ in range(50):
        names = kinesis.rpc("ListStreams", {}).get("StreamNames", [])
        if stream not in names:
            break
        time.sleep(0.2)
    assert stream not in kinesis.rpc("ListStreams", {}).get("StreamNames", [])
