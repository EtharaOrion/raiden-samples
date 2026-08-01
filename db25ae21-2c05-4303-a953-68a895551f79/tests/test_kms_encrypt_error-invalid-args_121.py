def test_encrypt_invalid_key_usage_signing_key(cli, kms):
    created = kms.rpc("CreateKey", {
        "KeyUsage": "SIGN_VERIFY",
        "KeySpec": "RSA_2048",
    })
    key_id = created["KeyMetadata"]["KeyId"]

    assert kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["KeyUsage"] == "SIGN_VERIFY"

    import base64
    plaintext = base64.b64encode(b"secret data").decode()

    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidKeyUsageException" in result.stderr

    # key still describes fine and remains a signing key
    md = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert md["KeyUsage"] == "SIGN_VERIFY"