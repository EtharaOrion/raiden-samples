def test_untag_resource_removes_specified_tag(cli, kms, tmp_path):
    import json

    created = kms.rpc("CreateKey", {"Description": "untag-resource test key"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc(
        "TagResource",
        {
            "KeyId": key_id,
            "Tags": [
                {"TagKey": "remove-me", "TagValue": "temporary"},
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
        json.dumps(["remove-me"]),
    )

    assert result.returncode == 0

    listed = kms.rpc("ListResourceTags", {"KeyId": key_id})
    tags = {tag["TagKey"]: tag["TagValue"] for tag in listed["Tags"]}
    assert "remove-me" not in tags
    assert tags["keep-me"] == "retained"