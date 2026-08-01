def test_describe_key_error_nonexistent(cli, kms, tmp_path):
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Ensure the key does not exist in kms state.
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        raised = False
    except Exception:
        raised = True
    assert raised, "precondition failed: key unexpectedly exists"

    result = cli("kms", "describe-key", "--key-id", missing_key_id)

    assert result.returncode != 0
    assert "NotFound" in result.stderr