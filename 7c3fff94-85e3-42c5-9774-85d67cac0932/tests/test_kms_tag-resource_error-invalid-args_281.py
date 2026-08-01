def test_tag_resource_rejects_empty_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "empty key-id tag test"})
    key_id = created["KeyMetadata"]["KeyId"]

    original_tag = {"TagKey": "existing", "TagValue": "unchanged"}
    kms.rpc("TagResource", {"KeyId": key_id, "Tags": [original_tag]})
    before = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert original_tag in before["Tags"]

    result = cli(
        "kms",
        "tag-resource",
        "--key-id",
        "",
        "--tags",
        '[{"TagKey":"attempted","TagValue":"new"}]',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    after = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert original_tag in after["Tags"]
    assert {"TagKey": "attempted", "TagValue": "new"} not in after["Tags"]