from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_negative_get_missing_table_after_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_ngmt1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_ngmt1",
                 "--item", '{"pk":{"S":"n1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_ngmt1_other",
                 "--key", '{"pk":{"S":"n1"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
