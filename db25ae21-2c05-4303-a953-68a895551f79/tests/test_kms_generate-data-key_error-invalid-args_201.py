def test_generate_data_key_invalid_key_usage(cli, kms):
    # Seed a key intended for signing/verification, not encryption
    created = kms.rpc("CreateKey", {
        "KeyUsage": "SIGN_VERIFY",
        "KeySpec": "RSA_2048",
    })
    key_id = created["KeyMetadata"]["KeyId"]

    # Sanity: key exists with the non-encrypt usage
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyUsage"] == "SIGN_VERIFY"

    # GenerateDataKey against a SIGN_VERIFY key must fail with InvalidKeyUsageException
    result = cli("kms", "generate-data-key", "--key-id", key_id, "--key-spec", "AES_256")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidKeyUsageException" in result.stderr

    # State unchanged: key still present with same usage
    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyId"] == key_id
    assert after["KeyMetadata"]["KeyUsage"] == "SIGN_VERIFY"