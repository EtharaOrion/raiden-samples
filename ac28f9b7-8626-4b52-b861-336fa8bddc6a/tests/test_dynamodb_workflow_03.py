from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_updateitem_missing_table_fails(cli, ddb_client):
    result = cli("dynamodb", "describe-limits")
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "NoSuchTableWf4",
                 "--key", '{"pk":{"S":"x"}}',
                 "--update-expression", "SET a = :v",
                 "--expression-attribute-values", '{":v":{"S":"z"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
