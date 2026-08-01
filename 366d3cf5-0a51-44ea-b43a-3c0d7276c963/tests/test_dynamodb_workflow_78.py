from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_delete_recreate_check_empty(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf79",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf79", "--item", '{"pk":{"S":"a"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="Wf79", Key={"pk": {"S": "a"}})
    result = cli("dynamodb", "delete-table", "--table-name", "Wf79")
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "Wf79",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf79", Key={"pk": {"S": "a"}})
