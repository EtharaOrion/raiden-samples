def test_tag_resource_nonexistent_key_returns_not_found(cli, kms):
    existing = kms.rpc("CreateKey", {"Description": "tag-resource error sentinel"})
    existing_key_id = existing["KeyMetadata"]["KeyId"]

    sentinel_tag = {"TagKey": "sentinel", "TagValue": "preserved"}
    kms.rpc("TagResource", {"KeyId": existing_key_id, "Tags": [sentinel_tag]})

    keys_before = kms.rpc("ListKeys", {})["Keys"]
    existing_ids = {key["KeyId"] for key in keys_before}
    candidates = [
        "00000000-0000-4000-8000-000000000001",
        "00000000-0000-4000-8000-000000000002",
    ]
    missing_key_id = next(candidate for candidate in candidates if candidate not in existing_ids)

    tags_before = kms.rpc("ListResourceTags", {"KeyId": existing_key_id})["Tags"]
    assert sentinel_tag in tags_before

    result = cli(
        "kms",
        "tag-resource",
        "--key-id",
        missing_key_id,
        "--tags",
        '[{"TagKey":"attempted","TagValue":"not-applied"}]',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    keys_after = kms.rpc("ListKeys", {})["Keys"]
    assert missing_key_id not in {key["KeyId"] for key in keys_after}

    tags_after = kms.rpc("ListResourceTags", {"KeyId": existing_key_id})["Tags"]
    assert {(tag["TagKey"], tag["TagValue"]) for tag in tags_after} == {
        (tag["TagKey"], tag["TagValue"]) for tag in tags_before
    }