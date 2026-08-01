def test_encrypt_missing_key_id_fails_without_changing_kms_state(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "encrypt-invalid-args"})
    key_metadata = created["KeyMetadata"]
    key_id = key_metadata["KeyId"]

    result = cli("kms", "encrypt", "--plaintext", "dGVzdA==")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    current = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert current["KeyId"] == key_id
    assert current["KeyState"] == key_metadata["KeyState"]
    assert current["Enabled"] == key_metadata["Enabled"]