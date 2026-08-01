def test_describe_user_pool_rejects_invalid_attribute_definitions(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "invalid-describe-args-pool"})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "describe-user-pool",
        "--user-pool-id",
        pool_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "invalid-describe-args-pool"