def test_delete_user_pool_removes_pool(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "delete-me-pool"})
    pool_id = created["UserPool"]["Id"]

    pools_before = cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    assert any(p["Id"] == pool_id for p in pools_before)

    result = cli("cognito-idp", "delete-user-pool", "--user-pool-id", pool_id)
    assert result.returncode == 0

    pools_after = cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    assert all(p["Id"] != pool_id for p in pools_after)