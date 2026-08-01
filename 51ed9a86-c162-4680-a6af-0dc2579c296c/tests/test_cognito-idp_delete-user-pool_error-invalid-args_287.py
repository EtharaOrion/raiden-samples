def test_delete_user_pool_invalid_id_error(cli, cognito):
    bogus_id = "x" * 54
    result = cli("cognito-idp", "delete-user-pool", "--user-pool-id", bogus_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "NotFound" in result.stderr

    pools = cognito.rpc("ListUserPools", {"MaxResults": 60}).get("UserPools", [])
    assert all(p.get("Id") != bogus_id for p in pools)