def test_encrypt_missing_required_plaintext(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "encrypt missing plaintext argument test"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "encrypt", "--key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--plaintext" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == "encrypt missing plaintext argument test"
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"