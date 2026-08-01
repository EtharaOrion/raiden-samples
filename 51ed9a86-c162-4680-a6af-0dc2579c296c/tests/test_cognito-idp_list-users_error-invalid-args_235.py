def test_list_users_empty_pool_id_invalid(cli, cognito):
    result = cli("cognito-idp", "list-users", "--user-pool-id", "")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr
    assert (
        "InvalidParameterException" in stderr
        or "ResourceNotFoundException" in stderr
        or "ValidationException" in stderr
        or "Invalid length" in stderr
    )