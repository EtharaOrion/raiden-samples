def test_list_aliases_empty_key_id_invalid(cli, kms):
    result = cli("kms", "list-aliases", "--key-id", "")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    combined = (result.stderr + result.stderr.lower())
    assert ("Exception" in result.stderr
            or "NotFound" in result.stderr
            or "InvalidArn" in result.stderr
            or "ValidationException" in result.stderr
            or "validation" in result.stderr.lower())