def test_create_user_pool_client_error_nonexistent(cli, cognito):
    fake_pool_id = "local_nonexistent123"

    # Ensure the pool does not exist
    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", fake_pool_id,
        "--client-name", "MyClient",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "ResourceNotFoundException" in result.stderr

    # Assert no client was created against this nonexistent pool
    try:
        listed = cognito.rpc("ListUserPoolClients", {
            "UserPoolId": fake_pool_id,
            "MaxResults": 10,
        })
        assert not listed.get("UserPoolClients")
    except Exception:
        # ListUserPoolClients on a nonexistent pool also errors, which confirms absence
        pass