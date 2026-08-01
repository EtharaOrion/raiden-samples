def test_enable_key_nonexistent_key_id(cli, kms):
    # Use a well-formed but nonexistent key id so EnableKey fails
    missing_key_id = "00000000-0000-0000-0000-000000000000"

    # Sanity: the key should not exist prior to the call
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        pre_exists = True
    except Exception:
        pre_exists = False
    assert not pre_exists

    result = cli("kms", "enable-key", "--key-id", missing_key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    # Confirm the key still does not exist in kms state
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        post_exists = True
    except Exception:
        post_exists = False
    assert not post_exists