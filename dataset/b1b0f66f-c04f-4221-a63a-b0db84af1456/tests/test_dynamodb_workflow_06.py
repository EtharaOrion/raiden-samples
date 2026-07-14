from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding_multiple_items(cli, ddb_client):
    ddb_client.create_table(
        TableName="WFQuery1",
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
    ddb_client.put_item(TableName="WFQuery1", Item={"pk": {"S": "g"}, "sk": {"S": "a"}})
    ddb_client.put_item(TableName="WFQuery1", Item={"pk": {"S": "g"}, "sk": {"S": "b"}})
    ddb_client.put_item(TableName="WFQuery1", Item={"pk": {"S": "other"}, "sk": {"S": "c"}})
    result = cli(
        "dynamodb", "query",
        "--table-name", "WFQuery1",
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"g"}}',
    )
    assert result.returncode == 0
    import json
    out = json.loads(result.stdout)
    got = set()
    for it in out["Items"]:
        got.add((it["pk"]["S"], it["sk"]["S"]))
    assert got == {("g", "a"), ("g", "b")}
