from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_ddb_create_cli_put(cli, ddb_client, tmp_path):
    ddb_client.create_table(TableName="Wf45",
                            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                            BillingMode="PAY_PER_REQUEST")
    result = cli("dynamodb", "put-item", "--table-name", "Wf45", "--item", '{"pk":{"S":"v"},"n":{"N":"11"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf45", Key={"pk": {"S": "v"}})
    assert from_item(resp["Item"]) == {"pk": "v", "n": 11}
