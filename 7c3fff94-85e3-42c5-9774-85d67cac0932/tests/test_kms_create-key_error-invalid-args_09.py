def test_create_key_rejects_empty_xks_key_id(cli, kms):
    before = kms.rpc("ListKeys", {})
    before_key_ids = {key["KeyId"] for key in before["Keys"]}

    result = cli("kms", "create-key", "--xks-key-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    after = kms.rpc("ListKeys", {})
    after_key_ids = {key["KeyId"] for key in after["Keys"]}
    assert after_key_ids == before_key_ids