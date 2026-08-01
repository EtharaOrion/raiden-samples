def test_delete_user_pool_rejects_empty_user_pool_id(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-empty-id-test-pool"},
    )
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "delete-user-pool",
        "--user-pool-id",
        "",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "Invalid length" in result.stderr
        or "InvalidParameterException" in result.stderr
    )

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "delete-empty-id-test-pool"