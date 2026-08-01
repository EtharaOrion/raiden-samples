from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_query_by_pk(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf65Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf65Table",
                 "--item", '{"pk":{"S":"qp1"},"data":{"S":"hello"}}')
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf65Table",
        KeyConditionExpression="pk = :p",
        ExpressionAttributeValues={":p": {"S": "qp1"}},
    )
    items = [from_item(it) for it in resp["Items"]]
    assert items == [{"pk": "qp1", "data": "hello"}]
