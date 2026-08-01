def test_untag_resource_missing_key_id(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "untag-resource invalid args test"})
    key_id = key["KeyMetadata"]["KeyId"]

    kms.rpc(
        "TagResource",
        {
            "KeyId": key_id,
            "Tags": [{"TagKey": "preserved-tag", "TagValue": "preserved-value"}],
        },
    )

    result = cli(
        "kms",
        "untag-resource",
        "--tag-keys",
        '["preserved-tag"]',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    tags = kms.rpc("ListResourceTags", {"KeyId": key_id})["Tags"]
    assert {"TagKey": "preserved-tag", "TagValue": "preserved-value"} in tags