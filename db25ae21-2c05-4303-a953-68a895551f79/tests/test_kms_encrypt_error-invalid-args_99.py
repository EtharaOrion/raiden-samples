def test_encrypt_invalid_args(cli, kms):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    import base64
    plaintext = base64.b64encode(b"secret").decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    # Key state unchanged and still usable via a proper encrypt round-trip
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert desc["KeyState"] == "Enabled"
    assert desc["Enabled"] is True

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert dec["Plaintext"] == plaintext