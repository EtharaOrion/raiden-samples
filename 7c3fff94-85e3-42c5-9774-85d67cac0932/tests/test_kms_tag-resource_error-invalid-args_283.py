def test_tag_resource_rejects_unknown_invalid_argument_without_tagging(cli, kms, tmp_path):
    import json

    created = kms.rpc("CreateKey", {"Description": "tag-resource invalid args test"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc(
        "TagResource",
        {
            "KeyId": key_id,
            "Tags": [{"TagKey": "baseline", "TagValue": "preserved"}],
        },
    )
    before = kms.rpc("ListResourceTags", {"KeyId": key_id})
    before_tags = {
        (tag["TagKey"], tag["TagValue"])
        for tag in before["Tags"]
    }
    assert before_tags == {("baseline", "preserved")}

    result = cli(
        "kms",
        "tag-resource",
        "--key-id",
        key_id,
        "--tags",
        json.dumps([{"TagKey": "candidate", "TagValue": "must-not-be-added"}]),
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("ListResourceTags", {"KeyId": key_id})
    after_tags = {
        (tag["TagKey"], tag["TagValue"])
        for tag in after["Tags"]
    }
    assert after_tags == before_tags
    assert ("candidate", "must-not-be-added") not in after_tags