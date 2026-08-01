def test_list_streams_exclusive_start_stream_name(cli, kinesis):
    seed_first = "aaa-seed-stream"
    seed_after = "zzz-target-stream"
    for name in (seed_first, seed_after):
        try:
            kinesis.rpc("CreateStream", {"StreamName": name, "ShardCount": 1})
        except Exception:
            pass

    listed = kinesis.rpc("ListStreams", {})
    assert seed_first in listed["StreamNames"]
    assert seed_after in listed["StreamNames"]

    result = cli(
        "kinesis", "list-streams",
        "--exclusive-start-stream-name", seed_first,
    )
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    assert "StreamNames" in payload
    assert isinstance(payload["StreamNames"], list)
    # The exclusive-start stream itself must NOT be included in the results.
    assert seed_first not in payload["StreamNames"]
    # A stream sorted after the start name should still be listed.
    assert seed_after in payload["StreamNames"]

    for name in (seed_first, seed_after):
        try:
            kinesis.rpc("DeleteStream", {"StreamName": name})
        except Exception:
            pass