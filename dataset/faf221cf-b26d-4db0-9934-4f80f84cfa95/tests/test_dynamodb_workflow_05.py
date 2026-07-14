from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import from_item


def test_workflow_put_missing_table_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "put-item", "--table-name", "NoSuchTablePut1",
                 "--item", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "NoSuchTablePut1" not in ddb_client.list_tables()["TableNames"]
