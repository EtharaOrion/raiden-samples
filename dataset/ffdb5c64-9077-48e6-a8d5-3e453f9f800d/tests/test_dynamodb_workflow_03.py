from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblQuery",
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
    for sk in ("s1", "s2", "s3"):
        result = cli("dynamodb", "put-item", "--table-name", "WfTblQuery",
                     "--item", '{"pk":{"S":"grp"},"sk":{"S":"%s"}}' % sk)
        assert result.returncode == 0
    result = cli("dynamodb", "query", "--table-name", "WfTblQuery",
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"grp"}}')
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="WfTblQuery",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "grp"}},
    )
    got = {i["sk"]["S"] for i in resp["Items"]}
    assert got == {"s1", "s2", "s3"}
