def test_untag_resource_nonexistent_key(cli, kms, tmp_path):
    import uuid

    created = kms.rpc("CreateKey", {"Description": "untag-resource error control"})
    control_key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc(
        "TagResource",
        {
            "KeyId": control_key_id,
            "Tags": [{"TagKey": "protected", "TagValue": "unchanged"}],
        },
    )

    missing_key_id = str(uuid.uuid4())
    assert missing_key_id != control_key_id

    result = cli(
        "kms",
        "untag-resource",
        "--key-id",
        missing_key_id,
        "--tag-keys",
        '["protected"]',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    tags = kms.rpc("ListResourceTags", {"KeyId": control_key_id})["Tags"]
    assert {"TagKey": "protected", "TagValue": "unchanged"} in tags