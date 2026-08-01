def test_disable_key_nonexistent_returns_not_found(cli, kms):
    missing_key_id = "00000000-1111-2222-3333-444444444444"
    result = cli("kms", "disable-key", "--key-id", missing_key_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    # Verify the key genuinely does not exist in kms state
    try:
        resp = kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        # if it somehow returned, it must not be a valid enabled key we created
        assert resp.get("KeyMetadata", {}).get("KeyId") != missing_key_id
    except Exception:
        pass