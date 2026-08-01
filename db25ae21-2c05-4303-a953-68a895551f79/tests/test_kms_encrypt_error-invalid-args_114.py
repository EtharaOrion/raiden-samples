def test_encrypt_disabled_key_fails(cli, kms, tmp_path):
    import base64
    create = kms.rpc("CreateKey", {"Description": "disable-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    kms.rpc("DisableKey", {"KeyId": key_id})

    disabled = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert disabled["KeyMetadata"]["Enabled"] is False

    plaintext = base64.b64encode(b"secret data").decode()
    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "DisabledException" in result.stderr

    still = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert still["KeyMetadata"]["KeyState"] == "Disabled"
    assert still["KeyMetadata"]["Enabled"] is False