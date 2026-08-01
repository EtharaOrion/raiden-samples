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


def test_workflow_create_describe_list(cli, kinesis, tmp_path):
    """create-stream -> describe-stream -> list-streams, all through the CLI."""
    stream = "wf-create-describe-" + str(int(time.time() * 1000))

    c = cli("kinesis", "create-stream", "--stream-name", stream, "--shard-count", "1")
    assert c.returncode == 0, c.stderr

    sd = _wait_active(cli, stream)
    assert sd["StreamName"] == stream

    l = cli("kinesis", "list-streams")
    assert l.returncode == 0, l.stderr
    assert stream in json.loads(l.stdout)["StreamNames"]

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass
