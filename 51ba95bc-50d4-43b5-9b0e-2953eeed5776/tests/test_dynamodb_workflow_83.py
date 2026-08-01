from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_isolation_absent_in_second_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_iat1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_iat2",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_iat1",
                 "--item", '{"pk":{"S":"item1"},"v":{"S":"here"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_iat2",
                 "--key", '{"pk":{"S":"item1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_iat2", Key={"pk": {"S": "item1"}})
    assert "Item" not in resp
