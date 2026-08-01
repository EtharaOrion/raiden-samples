def test_encrypt_empty_key_id_rejected(cli, kms, tmp_path):
    # Establish a valid key so the server is in a working state; the command
    # under test still must fail purely because --key-id is empty.
    before = {k["KeyId"] for k in kms.rpc("ListKeys", {}).get("Keys", [])}

    result = cli("kms", "encrypt", "--key-id", "", "--plaintext", "aGVsbG8=")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr.lower()
    assert (
        "notfound" in stderr
        or "validation" in stderr
        or "invalid" in stderr
        or "exception" in stderr
    )

    # No new key was created as a side effect of the failed call.
    after = {k["KeyId"] for k in kms.rpc("ListKeys", {}).get("Keys", [])}
    assert after == before