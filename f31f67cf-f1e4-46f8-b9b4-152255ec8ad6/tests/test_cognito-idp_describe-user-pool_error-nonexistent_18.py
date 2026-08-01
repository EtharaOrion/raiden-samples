def test_describe_user_pool_nonexistent_returns_resource_not_found(cli, cognito):
    import uuid

    pool_name = f"describe-error-baseline-{uuid.uuid4().hex}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    existing_pool_id = created["UserPool"]["Id"]

    pool_id_prefix = existing_pool_id.rsplit("_", 1)[0]
    nonexistent_pool_id = f"{pool_id_prefix}_{uuid.uuid4().hex}"
    assert nonexistent_pool_id != existing_pool_id

    result = cli(
        "cognito-idp",
        "describe-user-pool",
        "--user-pool-id",
        nonexistent_pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    existing = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": existing_pool_id},
    )["UserPool"]
    assert existing["Id"] == existing_pool_id
    assert existing["Name"] == pool_name

    listed_ids = {
        pool["Id"]
        for pool in cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    }
    assert existing_pool_id in listed_ids
    assert nonexistent_pool_id not in listed_ids