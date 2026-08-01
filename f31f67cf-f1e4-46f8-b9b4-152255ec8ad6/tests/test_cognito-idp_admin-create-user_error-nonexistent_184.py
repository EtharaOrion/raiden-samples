def test_admin_create_user_nonexistent_pool(cli, cognito, tmp_path):
    pool_name = f"deleted-pool-{tmp_path.name}"
    username = f"missing-user-{tmp_path.name}"

    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    deleted_pool_id = created["UserPool"]["Id"]
    cognito.rpc("DeleteUserPool", {"UserPoolId": deleted_pool_id})

    result = cli(
        "cognito-idp",
        "admin-create-user",
        "--user-pool-id",
        deleted_pool_id,
        "--username",
        username,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    pools = cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    assert all(pool["Id"] != deleted_pool_id for pool in pools)