def test_tag_resource_rejects_unknown_flag_without_mutating_tags(cli, kms):
    key = kms.rpc("CreateKey", {
        "Description": "tag-resource invalid arguments test"
    })
    key_id = key["KeyMetadata"]["KeyId"]

    kms.rpc("TagResource", {
        "KeyId": key_id,
        "Tags": [{"TagKey": "existing", "TagValue": "preserved"}],
    })
    before = kms.rpc("ListResourceTags", {"KeyId": key_id})
    before_tags = {
        (tag["TagKey"], tag["TagValue"])
        for tag in before["Tags"]
    }

    result = cli(
        "kms",
        "tag-resource",
        "--key-id",
        key_id,
        "--tags",
        '[{"TagKey":"candidate","TagValue":"should-not-apply"}]',
        "--not-a-real-flag",
        "x",
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
    assert ("existing", "preserved") in after_tags
    assert ("candidate", "should-not-apply") not in after_tags