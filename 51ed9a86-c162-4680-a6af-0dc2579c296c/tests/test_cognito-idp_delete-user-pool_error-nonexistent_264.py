def test_delete_user_pool_nonexistent(cli, cognito):
    missing_pool_id = "local_nonexistent999"

    result = cli("cognito-idp", "delete-user-pool", "--user-pool-id", missing_pool_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Confirm no such pool exists in state
    pools = cognito.rpc("ListUserPools", {"MaxResults": 60}).get("UserPools", [])
    assert all(p.get("Id") != missing_pool_id for p in pools)