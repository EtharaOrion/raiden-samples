def test_encrypt_missing_required_plaintext(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {"Description": "encrypt-missing-plaintext"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "encrypt", "--key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    combined = (result.stderr + result.stderr.lower())
    assert "plaintext" in result.stderr.lower() or "required" in result.stderr.lower() or "argument" in result.stderr.lower()

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Enabled"] is True