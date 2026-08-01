from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_describe_limits_first_then_put_read(cli, ddb_client):
    result = cli("dynamodb", "describe-limits")
    assert result.returncode == 0
    ddb_client.create_table(
        TableName="Wf63Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf63Table",
                 "--item", '{"pk":{"S":"df1"},"n":{"N":"3"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf63Table", Key={"pk": {"S": "df1"}})
    assert from_item(resp["Item"])["n"] == 3
