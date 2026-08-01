def test_encrypt_empty_plaintext_invalid(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "encrypt-empty-plaintext"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Error" in result.stderr or "Exception" in result.stderr or "Invalid" in result.stderr

    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["Enabled"] is True