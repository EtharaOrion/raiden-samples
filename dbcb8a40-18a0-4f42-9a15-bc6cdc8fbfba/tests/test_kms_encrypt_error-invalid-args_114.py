def test_encrypt_disabled_key_fails(cli, kms, tmp_path):
    import json, base64

    create = kms.rpc("CreateKey", {"Description": "disabled-encrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    kms.rpc("DisableKey", {"KeyId": key_id})

    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["Enabled"] is False

    plaintext = base64.b64encode(b"secret data").decode()
    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "DisabledException" in result.stderr

    # Key still describes fine and remains disabled
    desc2 = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc2["KeyMetadata"]["Enabled"] is False