def test_update_key_description_happy_path(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "description before update"},
    )
    key_id = created["KeyMetadata"]["KeyId"]
    assert created["KeyMetadata"]["Description"] == "description before update"

    result = cli(
        "kms",
        "update-key-description",
        "--key-id",
        key_id,
        "--description",
        "description after update",
    )

    assert result.returncode == 0
    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == "description after update"