def test_create_key_rejects_empty_custom_key_store_id(cli, kms):
    before = kms.rpc("ListKeys", {})
    before_key_ids = {key["KeyId"] for key in before["Keys"]}

    result = cli("kms", "create-key", "--custom-key-store-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation failed" in result.stderr

    after = kms.rpc("ListKeys", {})
    after_key_ids = {key["KeyId"] for key in after["Keys"]}
    assert after_key_ids == before_key_ids