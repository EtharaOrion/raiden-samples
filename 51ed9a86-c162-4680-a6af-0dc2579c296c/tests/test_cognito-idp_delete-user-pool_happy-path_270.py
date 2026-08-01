def test_delete_user_pool_happy_path(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "pool-to-delete"})
    pool_id = created["UserPool"]["Id"]

    # sanity: pool exists before deletion
    before = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert any(p["Id"] == pool_id for p in before.get("UserPools", []))

    result = cli("cognito-idp", "delete-user-pool", "--user-pool-id", pool_id)
    assert result.returncode == 0

    after = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert all(p["Id"] != pool_id for p in after.get("UserPools", []))