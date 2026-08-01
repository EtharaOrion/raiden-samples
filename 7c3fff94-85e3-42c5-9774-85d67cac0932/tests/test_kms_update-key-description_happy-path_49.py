def test_update_key_description_happy_path(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "description before CLI update"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert before["KeyMetadata"]["Description"] == "description before CLI update"

    result = cli(
        "kms",
        "update-key-description",
        "--key-id",
        key_id,
        "--description",
        "description updated by CLI",
    )
    assert result.returncode == 0

    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyId"] == key_id
    assert after["KeyMetadata"]["Description"] == "description updated by CLI"