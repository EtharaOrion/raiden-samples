def test_encrypt_missing_required_key_id(cli, kms, tmp_path):
    # Sanity: a valid key exists in the backend, proving encrypt could work if key-id were given
    created = kms.rpc("CreateKey", {"Description": "encrypt-missing-keyid"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert key_id

    # Invoke encrypt WITHOUT the required --key-id option
    result = cli("kms", "encrypt", "--plaintext", "aGVsbG8=")

    # Must fail because --key-id is required
    assert result.returncode != 0
    assert "key-id" in result.stderr.lower()

    # State assertion: the pre-existing key is still intact and encryptable when used correctly
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Enabled"] is True

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": "aGVsbG8="})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert dec["Plaintext"] == "aGVsbG8="