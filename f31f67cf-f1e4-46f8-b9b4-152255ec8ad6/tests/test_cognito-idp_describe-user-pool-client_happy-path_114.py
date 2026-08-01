def test_describe_user_pool_client_happy_path(cli, cognito, tmp_path):
    import json

    suffix = tmp_path.name.replace("-", "")
    pool_name = f"describe-client-pool-{suffix}"
    client_name = f"describe-client-{suffix}"

    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    user_pool_id = pool["Id"]

    created_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": user_pool_id,
            "ClientName": client_name,
        },
    )["UserPoolClient"]
    client_id = created_client["ClientId"]

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--user-pool-id",
        user_pool_id,
        "--client-id",
        client_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["UserPoolClient"]["ClientId"] == client_id
    assert output["UserPoolClient"]["ClientName"] == client_name
    assert output["UserPoolClient"]["UserPoolId"] == user_pool_id

    stored_client = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": user_pool_id,
            "ClientId": client_id,
        },
    )["UserPoolClient"]
    assert stored_client["ClientId"] == client_id
    assert stored_client["ClientName"] == client_name
    assert stored_client["UserPoolId"] == user_pool_id