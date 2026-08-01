def test_generate_data_key_empty_key_id_rejected(cli, kms):
    before = kms.rpc("ListKeys", {})
    result = cli("kms", "generate-data-key", "--key-id", "")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr.lower()
    assert "notfound" in stderr or "validation" in stderr or "exception" in stderr
    after = kms.rpc("ListKeys", {})
    assert len(after.get("Keys", [])) == len(before.get("Keys", []))