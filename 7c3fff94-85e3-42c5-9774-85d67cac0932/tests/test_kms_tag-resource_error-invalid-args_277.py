def test_tag_resource_missing_required_tags(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "tag-resource invalid args test"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc(
        "TagResource",
        {
            "KeyId": key_id,
            "Tags": [{"TagKey": "existing", "TagValue": "unchanged"}],
        },
    )
    before = kms.rpc("ListResourceTags", {"KeyId": key_id})["Tags"]

    result = cli("kms", "tag-resource", "--key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    after = kms.rpc("ListResourceTags", {"KeyId": key_id})["Tags"]
    assert after == before
    assert {"TagKey": "existing", "TagValue": "unchanged"} in after