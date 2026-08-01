def test_list_users_nonexistent_pool_errors(cli, cognito):
    # Seed a real pool so we know the environment is functional and isolated.
    created = cognito.rpc("CreateUserPool", {"PoolName": "seed-pool-for-list-users"})
    real_pool_id = created["UserPool"]["Id"]
    assert real_pool_id

    # Reference a pool id that does not exist -> service error.
    bogus_pool_id = "local_doesnotexist999"
    result = cli("cognito-idp", "list-users", "--user-pool-id", bogus_pool_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # The real pool should still exist and list without error (no user leak).
    listed = cognito.rpc("ListUsers", {"UserPoolId": real_pool_id})
    assert listed.get("Users", []) == []