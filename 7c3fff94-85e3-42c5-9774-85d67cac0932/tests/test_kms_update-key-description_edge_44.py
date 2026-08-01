def test_update_key_description_to_empty_string(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "description to be cleared"},
    )
    key_id = created["KeyMetadata"]["KeyId"]
    assert created["KeyMetadata"]["Description"] == "description to be cleared"

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