from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import from_item


def test_workflow_get_missing_table_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "get-item", "--table-name", "NoSuchTableGet1",
                 "--key", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "NoSuchTableGet1" not in ddb_client.list_tables()["TableNames"]
