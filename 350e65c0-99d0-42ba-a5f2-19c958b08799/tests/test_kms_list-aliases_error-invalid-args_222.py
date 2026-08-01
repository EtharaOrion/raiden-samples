def test_list_aliases_empty_key_id_rejected(cli, kms):
    result = cli("kms", "list-aliases", "--key-id", "")
    assert result.returncode != 0
    stderr = result.stderr.lower()
    assert (
        "notfound" in stderr
        or "invalidarn" in stderr
        or "validation" in stderr
        or "exception" in stderr
    )