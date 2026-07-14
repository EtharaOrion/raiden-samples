from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_query_reflects(cli, ddb_client):
    ddb_client.create_table(
        TableName="WFUpdQuery",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WFUpdQuery", Item={"pk": {"S": "k1"}, "cnt": {"N": "0"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "WFUpdQuery",
        "--key", '{"pk":{"S":"k1"}}',
        "--update-expression", "SET cnt = :c",
        "--expression-attribute-values", '{":c":{"N":"42"}}',
    )
    assert result.returncode == 0
    result2 = cli(
        "dynamodb", "query",
        "--table-name", "WFUpdQuery",
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"k1"}}',
    )
    assert result2.returncode == 0
    import json
    out = json.loads(result2.stdout)
    assert len(out["Items"]) == 1
    assert out["Items"][0]["cnt"]["N"] == "42"
