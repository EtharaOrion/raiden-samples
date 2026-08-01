from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_decimal_number(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf69Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf69Table",
                 "--item", '{"pk":{"S":"dec1"},"price":{"N":"9.99"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf69Table", Key={"pk": {"S": "dec1"}})
    assert resp["Item"]["price"]["N"] == "9.99"
