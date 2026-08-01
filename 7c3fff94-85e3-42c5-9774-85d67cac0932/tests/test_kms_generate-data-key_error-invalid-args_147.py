def test_generate_data_key_rejects_unknown_flag(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "key for invalid generate-data-key argument test"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "generate-data-key",
        "--key-id",
        key_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == "key for invalid generate-data-key argument test"
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"