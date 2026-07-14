from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_putitem_missing_table_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "put-item", "--table-name", "NoSuchTblPut1",
                 "--item", '{"pk":{"S":"a"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "NoSuchTblPut1" not in ddb_client.list_tables()["TableNames"]
