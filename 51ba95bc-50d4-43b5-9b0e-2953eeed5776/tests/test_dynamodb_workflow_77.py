from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_missing_table_put_does_not_create(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_mtdc1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_mtdc1_missing",
                 "--item", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "Tbl_mtdc1_missing" not in ddb_client.list_tables()["TableNames"]
