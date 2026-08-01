def test_update_key_description_happy_path(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "original description"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "update-key-description",
        "--key-id",
        key_id,
        "--description",
        "updated description",
    )

    assert result.returncode == 0
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Description"] == "updated description"