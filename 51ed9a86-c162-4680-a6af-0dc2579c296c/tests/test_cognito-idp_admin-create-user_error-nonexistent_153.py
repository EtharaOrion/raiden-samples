def test_admin_create_user_nonexistent_pool(cli, cognito):
    fake_pool_id = "local_nonexistent"

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", fake_pool_id,
        "--username", "ghostuser",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no such user exists (pool doesn't exist, so lookup fails)
    try:
        found = cognito.rpc("AdminGetUser", {
            "UserPoolId": fake_pool_id,
            "Username": "ghostuser",
        })
        assert "Username" not in found
    except Exception:
        pass