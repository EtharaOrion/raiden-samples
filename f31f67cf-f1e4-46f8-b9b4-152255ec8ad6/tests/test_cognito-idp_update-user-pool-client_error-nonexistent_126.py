def test_update_user_pool_client_nonexistent_client(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-client-nonexistent-pool"},
    )["UserPool"]
    existing_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "existing-client",
        },
    )["UserPoolClient"]

    missing_client_id = "0" * 26
    if missing_client_id == existing_client["ClientId"]:
        missing_client_id = "1" * 26

    result = cli(
        "cognito-idp",
        "update-user-pool-client",
        "--user-pool-id",
        pool["Id"],
        "--client-id",
        missing_client_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": existing_client["ClientId"],
        },
    )["UserPoolClient"]
    assert described["ClientId"] == existing_client["ClientId"]
    assert described["ClientName"] == "existing-client"
    assert described["UserPoolId"] == pool["Id"]

    listed = cognito.rpc(
        "ListUserPoolClients",
        {
            "UserPoolId": pool["Id"],
            "MaxResults": 60,
        },
    )["UserPoolClients"]
    client_ids = {client["ClientId"] for client in listed}
    assert existing_client["ClientId"] in client_ids
    assert missing_client_id not in client_ids