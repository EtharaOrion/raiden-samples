from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_multiple_items(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf3Tbl",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf3Tbl",
                 "--item", '{"pk":{"S":"g1"},"sk":{"S":"s1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf3Tbl",
                 "--item", '{"pk":{"S":"g1"},"sk":{"S":"s2"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf3Tbl",
                 "--item", '{"pk":{"S":"g2"},"sk":{"S":"s3"}}')
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf3Tbl",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "g1"}},
    )
    got = {i["sk"]["S"] for i in resp["Items"]}
    assert got == {"s1", "s2"}
