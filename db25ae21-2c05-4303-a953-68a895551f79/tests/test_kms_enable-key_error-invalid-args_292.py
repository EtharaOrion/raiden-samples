def test_enable_key_missing_key_id(cli, kms):
    before = kms.rpc("ListKeys", {})
    before_ids = {k["KeyId"] for k in before.get("Keys", [])}

    result = cli("kms", "enable-key")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "key-id" in result.stderr.lower() or "required" in result.stderr.lower()

    after = kms.rpc("ListKeys", {})
    after_ids = {k["KeyId"] for k in after.get("Keys", [])}
    assert after_ids == before_ids