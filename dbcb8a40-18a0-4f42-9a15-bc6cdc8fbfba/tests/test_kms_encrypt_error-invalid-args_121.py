def test_encrypt_invalid_key_usage(cli, kms, tmp_path):
    # Seed a key with KeyUsage SIGN_VERIFY (cannot be used for Encrypt)
    created = kms.rpc("CreateKey", {
        "KeyUsage": "SIGN_VERIFY",
        "KeySpec": "RSA_2048",
        "Description": "sign-only key for encrypt-error test",
    })
    key_id = created["KeyMetadata"]["KeyId"]
    assert created["KeyMetadata"]["KeyUsage"] == "SIGN_VERIFY"

    # Attempt to encrypt with a SIGN_VERIFY key -> InvalidKeyUsageException
    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", "aGVsbG8=")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidKeyUsageException" in result.stderr

    # State assertion: key still exists and is unchanged/usable for signing
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["KeyUsage"] == "SIGN_VERIFY"