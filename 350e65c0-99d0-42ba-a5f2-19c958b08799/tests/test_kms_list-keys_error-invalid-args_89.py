def test_list_keys_limit_exceeds_maximum(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "list-keys limit validation"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "list-keys", "--limit", "1001")

    assert result.returncode != 0
    assert "ValidationException" in result.stderr or "Value" in result.stderr

    # Key state is unaffected and still describable
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id