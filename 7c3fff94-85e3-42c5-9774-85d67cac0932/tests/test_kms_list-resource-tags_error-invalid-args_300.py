def test_list_resource_tags_requires_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "list-resource-tags invalid args"})
    key_id = created["KeyMetadata"]["KeyId"]
    expected_tag = {"TagKey": "environment", "TagValue": "test"}

    kms.rpc("TagResource", {"KeyId": key_id, "Tags": [expected_tag]})

    result = cli("kms", "list-resource-tags")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    state = kms.rpc("ListResourceTags", {"KeyId": key_id})
    assert expected_tag in state["Tags"]