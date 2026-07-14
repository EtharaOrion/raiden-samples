from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf_Query",
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
    for sk in ["s1", "s2", "s3"]:
        result = cli("dynamodb", "put-item", "--table-name", "Wf_Query",
                     "--item", '{"pk":{"S":"P"},"sk":{"S":"' + sk + '"}}')
        assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf_Query",
                 "--item", '{"pk":{"S":"Other"},"sk":{"S":"x"}}')
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf_Query",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "P"}},
    )
    got = set(from_item(i)["sk"] for i in resp["Items"])
    assert got == {"s1", "s2", "s3"}
