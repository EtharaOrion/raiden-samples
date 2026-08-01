from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_after_overwrite(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf73",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf73", "--item", '{"pk":{"S":"k"},"v":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf73", "--item", '{"pk":{"S":"k"},"v":{"N":"2"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf73", "--key", '{"pk":{"S":"k"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf73", Key={"pk": {"S": "k"}})
