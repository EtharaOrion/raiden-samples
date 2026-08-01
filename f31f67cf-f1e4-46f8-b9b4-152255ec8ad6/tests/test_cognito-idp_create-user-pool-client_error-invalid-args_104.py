def test_create_user_pool_client_rejects_invalid_attribute_definitions(cli, cognito, tmp_path):
    pool_name = "invalid-args-pool-" + tmp_path.name
    client_name = "invalid-args-client"

    created_pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created_pool["UserPool"]["Id"]

    before = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    before_client_ids = {
        client["ClientId"] for client in before.get("UserPoolClients", [])
    }

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-name",
        client_name,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    after_clients = after.get("UserPoolClients", [])
    assert {client["ClientId"] for client in after_clients} == before_client_ids
    assert all(client["ClientName"] != client_name for client in after_clients)