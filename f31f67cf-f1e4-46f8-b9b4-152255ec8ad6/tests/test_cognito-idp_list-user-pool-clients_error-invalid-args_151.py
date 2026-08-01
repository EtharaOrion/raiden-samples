def test_list_user_pool_clients_rejects_empty_user_pool_id(cli, cognito, tmp_path):
    pool_name = f"pool-{tmp_path.name}"
    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    client_name = "existing-client"
    created_client = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": client_name},
    )["UserPoolClient"]
    client_id = created_client["ClientId"]

    result = cli(
        "cognito-idp",
        "list-user-pool-clients",
        "--user-pool-id",
        "",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    listed = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )["UserPoolClients"]
    assert any(
        item["ClientId"] == client_id and item["ClientName"] == client_name
        for item in listed
    )