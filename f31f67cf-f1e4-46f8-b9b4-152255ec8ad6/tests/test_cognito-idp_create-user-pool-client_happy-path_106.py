def test_create_user_pool_client_happy_path(cli, cognito, tmp_path):
    import json

    pool_name = f"pool-{tmp_path.name}"
    client_name = f"client-{tmp_path.name}"

    created_pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created_pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-name",
        client_name,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    output_client = output["UserPoolClient"]
    client_id = output_client["ClientId"]
    assert output_client["ClientName"] == client_name
    assert output_client["UserPoolId"] == pool_id

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )
    stored_client = described["UserPoolClient"]
    assert stored_client["ClientId"] == client_id
    assert stored_client["ClientName"] == client_name
    assert stored_client["UserPoolId"] == pool_id