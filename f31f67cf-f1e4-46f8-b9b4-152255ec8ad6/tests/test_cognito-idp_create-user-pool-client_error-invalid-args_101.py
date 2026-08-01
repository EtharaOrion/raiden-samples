def test_create_user_pool_client_rejects_empty_user_pool_id(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "invalid-client-pool"})["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    assert before.get("UserPoolClients", []) == []

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        "",
        "--client-name",
        "<string>",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length for parameter UserPoolId" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Name"] == "invalid-client-pool"

    after = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    assert after.get("UserPoolClients", []) == []