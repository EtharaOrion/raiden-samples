def test_list_users_nonexistent_pool_error(cli, cognito):
    # Reference a user pool ID that does not exist -> ResourceNotFoundException
    missing_pool_id = "local_doesnotexist999"

    result = cli("cognito-idp", "list-users", "--user-pool-id", missing_pool_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert underlying state: the pool truly does not exist
    pools = cognito.rpc("ListUserPools", {"MaxResults": 60})
    ids = [p["Id"] for p in pools.get("UserPools", [])]
    assert missing_pool_id not in ids