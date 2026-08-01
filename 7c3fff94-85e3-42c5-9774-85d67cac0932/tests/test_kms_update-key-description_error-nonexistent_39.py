def test_update_key_description_nonexistent(cli, kms, tmp_path):
    import uuid

    created = kms.rpc(
        "CreateKey",
        {"Description": "unchanged control key"},
    )
    control_key_id = created["KeyMetadata"]["KeyId"]

    before_metadata = kms.rpc(
        "DescribeKey",
        {"KeyId": control_key_id},
    )["KeyMetadata"]
    before_keys = kms.rpc("ListKeys", {})["Keys"]
    before_key_ids = {key["KeyId"] for key in before_keys}

    missing_key_id = str(uuid.uuid4())
    while missing_key_id in before_key_ids:
        missing_key_id = str(uuid.uuid4())

    result = cli(
        "kms",
        "update-key-description",
        "--key-id",
        missing_key_id,
        "--description",
        "must not be applied",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    after_metadata = kms.rpc(
        "DescribeKey",
        {"KeyId": control_key_id},
    )["KeyMetadata"]
    after_key_ids = {
        key["KeyId"] for key in kms.rpc("ListKeys", {})["Keys"]
    }

    assert after_metadata["Description"] == before_metadata["Description"]
    assert after_metadata["Description"] == "unchanged control key"
    assert after_key_ids == before_key_ids
    assert missing_key_id not in after_key_ids