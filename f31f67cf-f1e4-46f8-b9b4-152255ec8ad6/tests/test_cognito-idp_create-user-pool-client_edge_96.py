def test_create_user_pool_client_with_prevent_user_existence_errors(cli, cognito, tmp_path):
    import json

    pool_name = "pool-" + tmp_path.name
    client_name = "client-" + tmp_path.name

    created_pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created_pool["UserPool"]["Id"]

    initial_clients = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    assert initial_clients.get("UserPoolClients", []) == []

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-name",
        client_name,
        "--prevent-user-existence-errors",
        "ENABLED",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    output_client = output["UserPoolClient"]
    client_id = output_client["ClientId"]
    assert output_client["UserPoolId"] == pool_id
    assert output_client["ClientName"] == client_name
    assert output_client["PreventUserExistenceErrors"] == "ENABLED"

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )
    stored_client = described["UserPoolClient"]
    assert stored_client["ClientId"] == client_id
    assert stored_client["UserPoolId"] == pool_id
    assert stored_client["ClientName"] == client_name
    assert stored_client["PreventUserExistenceErrors"] == "ENABLED"