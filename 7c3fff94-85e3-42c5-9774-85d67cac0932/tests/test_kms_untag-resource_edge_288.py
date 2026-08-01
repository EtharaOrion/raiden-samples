def test_untag_resource_removes_only_specified_tag(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "untag-resource edge test"})
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

    before = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert {"TagKey": "remove-me", "TagValue": "obsolete"} in before["Tags"]
    assert {"TagKey": "keep-me", "TagValue": "retained"} in before["Tags"]

    result = cli(
        "kms",
        "untag-resource",
        "--key-id",
        key_id,
        "--tag-keys",
        "remove-me",
    )
    assert result.returncode == 0

    after = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert not any(tag["TagKey"] == "remove-me" for tag in after["Tags"])
    assert {"TagKey": "keep-me", "TagValue": "retained"} in after["Tags"]