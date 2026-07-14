from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seed(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfQry",
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
        result = cli("dynamodb", "put-item", "--table-name", "WfQry",
                     "--item", '{"pk":{"S":"grp"},"sk":{"S":"' + sk + '"}}')
        assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfQry",
                 "--item", '{"pk":{"S":"other"},"sk":{"S":"x1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "query", "--table-name", "WfQry",
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"grp"}}')
    assert result.returncode == 0
    items = ddb_client.query(
        TableName="WfQry",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "grp"}},
    )["Items"]
    got = set()
    for it in items:
        native = from_item(it)
        got.add((native["pk"], native["sk"]))
    assert got == {("grp", "s1"), ("grp", "s2"), ("grp", "s3")}
