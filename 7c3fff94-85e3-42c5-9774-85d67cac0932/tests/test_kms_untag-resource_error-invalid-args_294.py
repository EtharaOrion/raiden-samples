def test_untag_resource_rejects_empty_key_id_and_preserves_tags(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "untag-resource invalid args test"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc(
        "TagResource",
        {
            "KeyId": key_id,
            "Tags": [{"TagKey": "environment", "TagValue": "test"}],
        },
    )

    result = cli(
        "kms",
        "untag-resource",
        "--key-id",
        "",
        "--tag-keys",
        "<json>",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation failed" in result.stderr

    tags = kms.rpc("ListResourceTags", {"KeyId": key_id})["Tags"]
    assert {"TagKey": "environment", "TagValue": "test"} in tags