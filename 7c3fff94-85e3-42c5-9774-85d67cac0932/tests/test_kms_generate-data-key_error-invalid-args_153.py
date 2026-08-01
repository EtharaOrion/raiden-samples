def test_generate_data_key_rejects_invalid_attribute_definitions(cli, kms, tmp_path):
    created = kms.rpc(
        "CreateKey",
        {"Description": "generate-data-key invalid arguments test"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "generate-data-key",
        "--key-id",
        key_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == "generate-data-key invalid arguments test"
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"