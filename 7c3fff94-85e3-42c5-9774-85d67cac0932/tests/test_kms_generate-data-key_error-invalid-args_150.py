def test_generate_data_key_rejects_empty_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "key preserved after invalid generate-data-key request",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "generate-data-key", "--key-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation failed" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"