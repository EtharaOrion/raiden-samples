from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_missing_table_then_create_then_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_gmcg1",
                 "--key", '{"pk":{"S":"y"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_gmcg1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_gmcg1",
                 "--item", '{"pk":{"S":"y"},"v":{"S":"z"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_gmcg1", Key={"pk": {"S": "y"}})
    assert from_item(resp["Item"]) == {"pk": "y", "v": "z"}
