def test_delete_user_pool_nonexistent(cli, cognito):
    survivor = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-nonexistent-survivor"},
    )["UserPool"]
    deleted = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-nonexistent-target"},
    )["UserPool"]
    cognito.rpc("DeleteUserPool", {"UserPoolId": deleted["Id"]})

    result = cli(
        "cognito-idp",
        "delete-user-pool",
        "--user-pool-id",
        deleted["Id"],
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    remaining = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": survivor["Id"]},
    )["UserPool"]
    assert remaining["Id"] == survivor["Id"]
    assert remaining["Name"] == "delete-nonexistent-survivor"