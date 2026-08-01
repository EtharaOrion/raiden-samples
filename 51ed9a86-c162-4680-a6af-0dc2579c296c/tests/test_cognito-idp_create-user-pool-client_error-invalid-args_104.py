def test_create_user_pool_client_missing_client_name(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-pool-missing-client-name"})
    user_pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ClientName" in result.stderr or "required" in result.stderr.lower()

    # Assert no client was created in the pool
    listed = cognito.rpc("ListUserPoolClients", {"UserPoolId": user_pool_id, "MaxResults": 60})
    assert listed.get("UserPoolClients", []) == []