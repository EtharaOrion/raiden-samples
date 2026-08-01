def test_encrypt_empty_key_id_invalid_args(cli, kms):
    before = kms.rpc("ListKeys", {})
    key_ids_before = {k["KeyId"] for k in before.get("Keys", [])}

    result = cli("kms", "encrypt", "--key-id", "", "--plaintext", "aGVsbG8=")

    assert result.returncode != 0
    assert "NotFound" in result.stderr or "ValidationException" in result.stderr or "Invalid" in result.stderr

    after = kms.rpc("ListKeys", {})
    key_ids_after = {k["KeyId"] for k in after.get("Keys", [])}
    assert key_ids_after == key_ids_before