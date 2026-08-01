def test_list_resource_tags_rejects_unknown_attribute_definitions(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "list-resource-tags invalid args test"})
    key_id = created["KeyMetadata"]["KeyId"]

    expected_tag = {"TagKey": "environment", "TagValue": "test"}
    kms.rpc("TagResource", {"KeyId": key_id, "Tags": [expected_tag]})
    before = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert expected_tag in before["Tags"]

    result = cli(
        "kms",
        "list-resource-tags",
        "--key-id",
        key_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert after["Tags"] == before["Tags"]