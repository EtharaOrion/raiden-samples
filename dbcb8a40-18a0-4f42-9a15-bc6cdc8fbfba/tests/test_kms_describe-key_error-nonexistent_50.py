def test_describe_key_error_nonexistent(cli, kms, tmp_path):
    missing_id = "00000000-1111-2222-3333-444444444444"

    # Ensure the key does not exist in kms state
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_id})
        exists = True
    except Exception:
        exists = False
    assert not exists

    result = cli("kms", "describe-key", "--key-id", missing_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr