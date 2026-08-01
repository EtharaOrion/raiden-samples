def test_encrypt_invalid_key_usage(cli, kms, tmp_path):
    # Seed a SIGN_VERIFY asymmetric key which cannot be used for Encrypt
    created = kms.rpc("CreateKey", {
        "KeyUsage": "SIGN_VERIFY",
        "KeySpec": "RSA_2048",
        "Description": "sign-only key for invalid encrypt test",
    })
    key_id = created["KeyMetadata"]["KeyId"]
    assert created["KeyMetadata"]["KeyUsage"] == "SIGN_VERIFY"

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", "aGVsbG8gd29ybGQ=",
    )

    assert result.returncode != 0
    assert "InvalidKeyUsageException" in result.stderr

    # Key still describable and unchanged
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyUsage"] == "SIGN_VERIFY"