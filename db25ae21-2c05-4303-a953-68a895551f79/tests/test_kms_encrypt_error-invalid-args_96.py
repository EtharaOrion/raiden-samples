def test_encrypt_missing_required_plaintext(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "encrypt-missing-plaintext"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "encrypt", "--key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "plaintext" in result.stderr.lower()

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Enabled"] is True