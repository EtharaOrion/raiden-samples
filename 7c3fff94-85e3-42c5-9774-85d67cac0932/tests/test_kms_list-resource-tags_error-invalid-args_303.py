def test_list_resource_tags_rejects_unknown_flag(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "invalid-args tag test"})
    key_id = created["KeyMetadata"]["KeyId"]
    expected_tag = {"TagKey": "environment", "TagValue": "test"}

    kms.rpc("TagResource", {"KeyId": key_id, "Tags": [expected_tag]})

    result = cli(
        "kms",
        "list-resource-tags",
        "--key-id",
        key_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    tags = kms.rpc("ListResourceTags", {"KeyId": key_id})["Tags"]
    assert expected_tag in tags