from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_delete_get_cycle(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf41",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf41", "--item", '{"pk":{"S":"c"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="Wf41", Key={"pk": {"S": "c"}})
    result = cli("dynamodb", "delete-item", "--table-name", "Wf41", "--key", '{"pk":{"S":"c"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf41", Key={"pk": {"S": "c"}})
