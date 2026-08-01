def test_admin_get_user_nonexistent_pool(cli, cognito):
    fake_pool_id = "local_nonexistent999"
    result = cli(
        "cognito-idp", "admin-get-user",
        "--user-pool-id", fake_pool_id,
        "--username", "someuser",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    pools = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert all(p["Id"] != fake_pool_id for p in pools.get("UserPools", []))