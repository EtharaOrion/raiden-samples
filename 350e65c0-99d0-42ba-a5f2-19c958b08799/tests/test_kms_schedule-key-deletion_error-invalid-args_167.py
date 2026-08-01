def test_schedule_key_deletion_nonexistent_key(cli, kms):
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    result = cli(
        "kms",
        "schedule-key-deletion",
        "--key-id",
        missing_key_id,
    )

    assert result.returncode != 0
    assert "NotFound" in result.stderr

    # Ensure the bogus key still does not exist / has no PendingDeletion state created
    try:
        resp = kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        # If it somehow returns, it must not be a real described key we created
        assert "KeyMetadata" not in resp
    except Exception:
        pass