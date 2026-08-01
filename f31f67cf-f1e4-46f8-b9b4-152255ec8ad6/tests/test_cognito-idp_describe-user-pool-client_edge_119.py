def test_describe_user_pool_client_existing_client(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "describe-client-edge-pool"})["UserPool"]
    client_name = "x" * 128
    created_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": client_name,
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--user-pool-id",
        pool["Id"],
        "--client-id",
        created_client["ClientId"],
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["UserPoolClient"]["UserPoolId"] == pool["Id"]
    assert output["UserPoolClient"]["ClientId"] == created_client["ClientId"]
    assert output["UserPoolClient"]["ClientName"] == client_name

    stored_client = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": created_client["ClientId"],
        },
    )["UserPoolClient"]
    assert stored_client["UserPoolId"] == pool["Id"]
    assert stored_client["ClientId"] == created_client["ClientId"]
    assert stored_client["ClientName"] == client_name