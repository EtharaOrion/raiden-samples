from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_empty_string_value(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf38Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf38Table",
                 "--item", '{"pk":{"S":"es1"},"note":{"S":""}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf38Table", Key={"pk": {"S": "es1"}})
    assert from_item(resp["Item"])["note"] == ""
