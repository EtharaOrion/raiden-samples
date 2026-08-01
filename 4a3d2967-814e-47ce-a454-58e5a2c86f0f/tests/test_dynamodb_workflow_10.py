from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_projection(cli, ddb_client, tmp_path):
    t = "wf_proj_11"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}, "x": {"S": "1"}, "y": {"S": "2"}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"a"}}',
             "--projection-expression", "x")
    assert r1.returncode == 0
    items = json.loads(r1.stdout)["Items"]
    assert len(items) == 1
    assert "y" not in items[0]
    assert ddb_client.get_item(TableName=t, Key={"pk": {"S": "a"}})["Item"]["y"]["S"] == "2"
