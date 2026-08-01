def test_admin_create_user_invalid_user_pool_id(cli, cognito):
    bad_pool_id = "x" * 600
    username = "testuser"

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", bad_pool_id,
        "--username", username,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr

    # Assert no such pool exists / user was not created anywhere reachable.
    # Since the pool id is invalid, attempting to describe it must also fail.
    try:
        cognito.rpc("AdminGetUser", {"UserPoolId": bad_pool_id, "Username": username})
        got_user = True
    except Exception:
        got_user = False
    assert got_user is False