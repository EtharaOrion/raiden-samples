def test_untag_resource_missing_tag_keys_preserves_tags(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "untag-resource invalid args test"})
    key_id = created["KeyMetadata"]["KeyId"]

    expected_tag = {"TagKey": "environment", "TagValue": "test"}
    kms.rpc("TagResource", {"KeyId": key_id, "Tags": [expected_tag]})

    result = cli("kms", "untag-resource", "--key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--tag-keys" in result.stderr

    state = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert expected_tag in state["Tags"]