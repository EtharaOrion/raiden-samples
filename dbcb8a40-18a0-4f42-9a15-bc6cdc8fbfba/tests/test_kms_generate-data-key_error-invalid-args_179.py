def test_generate_data_key_error_invalid_args(cli, kms):
    created = kms.rpc("CreateKey", {})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    # key remains intact and usable
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["KeyState"] == "Enabled"

    dk = kms.rpc("GenerateDataKey", {"KeyId": key_id, "KeySpec": "AES_256"})
    assert dk["KeyId"].endswith(key_id) or dk["KeyId"] == key_id
    assert "Plaintext" in dk
    assert "CiphertextBlob" in dk