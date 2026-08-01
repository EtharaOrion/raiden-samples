def test_untag_resource_rejects_unknown_attribute_definitions(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "invalid untag arguments test"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc(
        "TagResource",
        {
            "KeyId": key_id,
            "Tags": [{"TagKey": "protected", "TagValue": "keep-me"}],
        },
    )
    before = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert {"TagKey": "protected", "TagValue": "keep-me"} in before["Tags"]

    result = cli(
        "kms",
        "untag-resource",
        "--key-id",
        key_id,
        "--tag-keys",
        '["protected"]',
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert {"TagKey": "protected", "TagValue": "keep-me"} in after["Tags"]