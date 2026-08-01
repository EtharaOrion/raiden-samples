def test_untag_resource_rejects_unknown_flag(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "invalid-args untag test"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc(
        "TagResource",
        {
            "KeyId": key_id,
            "Tags": [{"TagKey": "keep-me", "TagValue": "original-value"}],
        },
    )

    result = cli(
        "kms",
        "untag-resource",
        "--key-id",
        key_id,
        "--tag-keys",
        '["keep-me"]',
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    tags = kms.rpc("ListResourceTags", {"KeyId": key_id})["Tags"]
    assert {"TagKey": "keep-me", "TagValue": "original-value"} in tags