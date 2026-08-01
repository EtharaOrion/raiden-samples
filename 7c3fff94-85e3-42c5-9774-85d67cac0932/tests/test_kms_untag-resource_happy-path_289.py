def test_untag_resource_removes_specified_tag(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "untag-resource test"})
    key_id = key["KeyMetadata"]["KeyId"]

    kms.rpc(
        "TagResource",
        {
            "KeyId": key_id,
            "Tags": [
                {"TagKey": "remove-me", "TagValue": "temporary"},
                {"TagKey": "keep-me", "TagValue": "persistent"},
            ],
        },
    )

    before = kms.rpc("ListResourceTags", {"KeyId": key_id})
    before_tags = {tag["TagKey"]: tag["TagValue"] for tag in before["Tags"]}
    assert before_tags["remove-me"] == "temporary"
    assert before_tags["keep-me"] == "persistent"

    result = cli(
        "kms",
        "untag-resource",
        "--key-id",
        key_id,
        "--tag-keys",
        '["remove-me"]',
    )
    assert result.returncode == 0

    after = kms.rpc("ListResourceTags", {"KeyId": key_id})
    after_tags = {tag["TagKey"]: tag["TagValue"] for tag in after["Tags"]}
    assert "remove-me" not in after_tags
    assert after_tags["keep-me"] == "persistent"