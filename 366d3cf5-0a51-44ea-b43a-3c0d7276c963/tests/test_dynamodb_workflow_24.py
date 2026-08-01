from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_ddbput_cli_delete(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf25",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="Wf25", Item={"pk": {"S": "seed"}})
    result = cli("dynamodb", "delete-item", "--table-name", "Wf25", "--key", '{"pk":{"S":"seed"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf25", Key={"pk": {"S": "seed"}})
