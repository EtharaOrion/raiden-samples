def test_update_key_description_missing_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "original description"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert before["KeyMetadata"]["Description"] == "original description"

    result = cli(
        "kms",
        "update-key-description",
        "--description",
        "updated description",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyId"] == key_id
    assert after["KeyMetadata"]["Description"] == "original description"