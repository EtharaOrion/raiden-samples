def test_update_user_pool_nonexistent(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-user-pool-nonexistent-sentinel"},
    )
    pool_id = created["UserPool"]["Id"]
    missing_pool_id = f"{pool_id}missing"

    result = cli(
        "cognito-idp",
        "update-user-pool",
        "--user-pool-id",
        missing_pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    sentinel = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert sentinel["Id"] == pool_id
    assert sentinel["Name"] == "update-user-pool-nonexistent-sentinel"