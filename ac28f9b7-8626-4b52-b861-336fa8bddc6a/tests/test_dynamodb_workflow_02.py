from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_putitem_missing_table_fails(cli, ddb_client):
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "NoSuchTableWf3",
                 "--item", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
