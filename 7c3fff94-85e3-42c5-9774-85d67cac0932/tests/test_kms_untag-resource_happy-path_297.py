def test_untag_resource_removes_requested_tag(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "untag-resource happy path"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc(
        "TagResource",
        {
            "KeyId": key_id,
            "Tags": [
                {"TagKey": "remove-me", "TagValue": "obsolete"},
                {"TagKey": "keep-me", "TagValue": "retained"},
            ],
        },
    )

    result = cli(
        "kms",
        "untag-resource",
        "--key-id",
        key_id,
        "--tag-keys",
        '["remove-me"]',
    )

    assert result.returncode == 0

    response = kms.rpc("ListResourceTags", {"KeyId": key_id})
    tags = {tag["TagKey"]: tag["TagValue"] for tag in response["Tags"]}
    assert "remove-me" not in tags
    assert tags["keep-me"] == "retained"