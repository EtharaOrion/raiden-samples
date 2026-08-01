from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_recreate_different_schema(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf35",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf35")
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "Wf35",
                 "--attribute-definitions", '[{"AttributeName":"id","AttributeType":"N"}]',
                 "--key-schema", '[{"AttributeName":"id","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf35", "--item", '{"id":{"N":"3"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="Wf35", Key={"id": {"N": "3"}})
