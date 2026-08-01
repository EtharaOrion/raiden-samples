def test_tag_resource_updates_tag_to_empty_value(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "tag-resource edge test"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc(
        "TagResource",
        {
            "KeyId": key_id,
            "Tags": [{"TagKey": "edge-empty-value", "TagValue": "previous-value"}],
        },
    )
    before = kms.rpc("ListResourceTags", {"KeyId": key_id})
    before_tags = {tag["TagKey"]: tag["TagValue"] for tag in before["Tags"]}
    assert before_tags["edge-empty-value"] == "previous-value"

    result = cli(
        "kms",
        "tag-resource",
        "--key-id",
        key_id,
        "--tags",
        '[{"TagKey":"edge-empty-value","TagValue":""}]',
    )
    assert result.returncode == 0

    after = kms.rpc("ListResourceTags", {"KeyId": key_id})
    after_tags = {tag["TagKey"]: tag["TagValue"] for tag in after["Tags"]}
    assert after_tags["edge-empty-value"] == ""