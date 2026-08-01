from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_nonexistent_key_leaves_others(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf31",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf31", "--item", '{"pk":{"S":"keep"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf31", "--key", '{"pk":{"S":"other"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="Wf31", Key={"pk": {"S": "keep"}})
