def test_describe_key_nonexistent_returns_not_found(cli, kms):
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    result = cli("kms", "describe-key", "--key-id", missing_key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    listed = kms.rpc("ListKeys", {})
    key_ids = [k["KeyId"] for k in listed.get("Keys", [])]
    assert missing_key_id not in key_ids