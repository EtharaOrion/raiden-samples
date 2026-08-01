def test_list_keys_invalid_empty_marker(cli, kms):
    # Seed prerequisite state so a valid ListKeys would return something.
    created = kms.rpc("CreateKey", {"Description": "marker-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert key_id

    # Run the command under test with an empty (invalid) marker.
    result = cli("kms", "list-keys", "--marker", "")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidMarker" in result.stderr or "Marker" in result.stderr

    # The key must still exist and be untouched.
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id