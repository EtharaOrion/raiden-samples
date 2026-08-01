from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_via_ddb_and_cli_overwrite(cli, ddb_client, tmp_path):
    ddb_client.create_table(TableName="Wf56",
                            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                            BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="Wf56", Item={"pk": {"S": "k"}, "v": {"S": "old"}})
    result = cli("dynamodb", "put-item", "--table-name", "Wf56", "--item", '{"pk":{"S":"k"},"v":{"S":"new"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf56", Key={"pk": {"S": "k"}})
    assert from_item(resp["Item"]) == {"pk": "k", "v": "new"}
