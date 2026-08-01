def test_tag_resource_happy_path_adds_tag(cli, kms):
    import uuid

    created = kms.rpc(
        "CreateKey",
        {"Description": "tag-resource-happy-" + uuid.uuid4().hex},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    tag_key = "k" + uuid.uuid4().hex
    tag_value = "v" + uuid.uuid4().hex
    result = cli(
        "kms",
        "tag-resource",
        "--key-id",
        key_id,
        "--tags",
        "TagKey=" + tag_key + ",TagValue=" + tag_value,
    )
    assert result.returncode == 0, result.stderr

    tags = kms.rpc("ListResourceTags", {"KeyId": key_id})["Tags"]
    assert any(
        t.get("TagKey") == tag_key and t.get("TagValue") == tag_value for t in tags
    )
