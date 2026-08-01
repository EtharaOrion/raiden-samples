def test_disable_key_disables_enabled_key(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "disable-key edge test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Ensure it starts enabled
    before = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert before["KeyMetadata"]["Enabled"] is True

    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode == 0

    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["Enabled"] is False
    assert after["KeyMetadata"]["KeyState"] == "Disabled"

    # A disabled key must reject cryptographic operations
    import base64
    encrypt = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", base64.b64encode(b"hello").decode(),
    )
    assert encrypt.returncode != 0
    assert "DisabledException" in encrypt.stderr