def test_update_key_description_empty_value(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "initial description"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "update-key-description",
        "--key-id",
        key_id,
        "--description",
        "",
    )

    assert result.returncode == 0
    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == ""