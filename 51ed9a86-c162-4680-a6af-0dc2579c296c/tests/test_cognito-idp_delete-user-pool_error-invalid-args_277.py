def test_delete_user_pool_invalid_pool_id(cli, cognito):
    invalid_pool_id = "x" * 800
    result = cli("cognito-idp", "delete-user-pool", "--user-pool-id", invalid_pool_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "NotFound" in result.stderr

    # Ensure no such pool exists in state
    pools = cognito.rpc("ListUserPools", {"MaxResults": 60})
    ids = [p["Id"] for p in pools.get("UserPools", [])]
    assert invalid_pool_id not in ids