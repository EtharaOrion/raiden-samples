def test_admin_create_user_nonexistent_pool(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "admin-create-user-nonexistent-pool"},
    )
    existing_pool_id = created["UserPool"]["Id"]

    prefix, suffix = existing_pool_id.rsplit("_", 1)
    replacement = "z" if suffix[-1] != "z" else "y"
    nonexistent_pool_id = prefix + "_" + suffix[:-1] + replacement

    pools_before = cognito.rpc("ListUserPools", {"MaxResults": 10})["UserPools"]
    assert existing_pool_id in {pool["Id"] for pool in pools_before}
    assert nonexistent_pool_id not in {pool["Id"] for pool in pools_before}
    assert cognito.rpc(
        "ListUsers",
        {"UserPoolId": existing_pool_id},
    )["Users"] == []

    result = cli(
        "cognito-idp",
        "admin-create-user",
        "--user-pool-id",
        nonexistent_pool_id,
        "--username",
        "nonexistent-pool-user",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    pools_after = cognito.rpc("ListUserPools", {"MaxResults": 10})["UserPools"]
    assert existing_pool_id in {pool["Id"] for pool in pools_after}
    assert nonexistent_pool_id not in {pool["Id"] for pool in pools_after}
    assert cognito.rpc(
        "ListUsers",
        {"UserPoolId": existing_pool_id},
    )["Users"] == []