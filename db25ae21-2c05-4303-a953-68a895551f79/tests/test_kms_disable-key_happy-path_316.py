def test_disable_key_happy_path(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "to-disable"})
    key_id = created["KeyMetadata"]["KeyId"]

    # Ensure it starts enabled
    pre = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert pre["KeyMetadata"]["Enabled"] is True

    result = cli("kms", "disable-key", "--key-id", key_id)
    assert result.returncode == 0

    post = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert post["KeyMetadata"]["Enabled"] is False

    # Disabled key cannot encrypt
    import base64
    enc = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", base64.b64encode(b"hello").decode(),
    )
    assert enc.returncode != 0
    assert "DisabledException" in enc.stderr