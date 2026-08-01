def test_update_key_description_happy_path(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "description-before-update"})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert before["KeyMetadata"]["Description"] == "description-before-update"

    result = cli(
        "kms",
        "update-key-description",
        "--key-id",
        key_id,
        "--description",
        "description-after-update",
    )
    assert result.returncode == 0

    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyId"] == key_id
    assert after["KeyMetadata"]["Description"] == "description-after-update"