def test_describe_user_pool_error_nonexistent(cli, cognito):
    missing_pool_id = "local_nonexistent999"

    pools = cognito.rpc("ListUserPools", {"MaxResults": 60}).get("UserPools", [])
    assert all(p.get("Id") != missing_pool_id for p in pools)

    result = cli("cognito-idp", "describe-user-pool", "--user-pool-id", missing_pool_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    pools_after = cognito.rpc("ListUserPools", {"MaxResults": 60}).get("UserPools", [])
    assert all(p.get("Id") != missing_pool_id for p in pools_after)