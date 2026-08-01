def test_update_user_pool_rejects_invalid_attribute_definitions(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "invalid-attribute-definitions-pool"},
    )
    pool_id = created["UserPool"]["Id"]
    before = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": pool_id},
    )["UserPool"]

    result = cli(
        "cognito-idp",
        "update-user-pool",
        "--user-pool-id",
        pool_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "Invalid JSON" in result.stderr

    after = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": pool_id},
    )["UserPool"]
    assert after == before
    assert after["Id"] == pool_id
    assert after["Name"] == "invalid-attribute-definitions-pool"