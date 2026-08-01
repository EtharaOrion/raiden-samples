def test_generate_data_key_invalid_key_usage(cli, kms, tmp_path):
    # Seed a key intended for signing/verification (not encryption),
    # which cannot be used to generate a data key.
    created = kms.rpc("CreateKey", {
        "KeyUsage": "SIGN_VERIFY",
        "KeySpec": "ECC_NIST_P256",
        "Description": "sign-only key for invalid usage test",
    })
    key_id = created["KeyMetadata"]["KeyId"]

    # Sanity: the key exists and has the wrong usage for GenerateDataKey.
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyUsage"] == "SIGN_VERIFY"

    # Attempt to generate a data key using a SIGN_VERIFY key -> must fail.
    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidKeyUsageException" in result.stderr

    # Key state is unchanged / still present after the failed operation.
    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyId"] == key_id
    assert after["KeyMetadata"]["KeyUsage"] == "SIGN_VERIFY"