def test_encrypt_disabled_key_returns_error(cli, kms, tmp_path):
    import base64, json

    create = kms.rpc("CreateKey", {"Description": "disabled-encrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    kms.rpc("DisableKey", {"KeyId": key_id})

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is False

    plaintext = base64.b64encode(b"secret data").decode()
    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)

    assert result.returncode != 0
    assert "DisabledException" in result.stderr

    # confirm state unchanged: key still exists and remains disabled
    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["Enabled"] is False