from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_recreate_put_delete(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf62",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf62")
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "Wf62",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf62", "--item", '{"pk":{"S":"a"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf62", "--key", '{"pk":{"S":"a"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf62", Key={"pk": {"S": "a"}})
