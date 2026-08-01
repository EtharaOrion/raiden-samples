from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_multiple_hash_disjoint(cli, ddb_client, tmp_path):
    t = "wf_disjoint_20"
    ddb_client.create_table(
        TableName=t,
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
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "A"}, "sk": {"S": "x"}})
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "A"}, "sk": {"S": "y"}})
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "B"}, "sk": {"S": "z"}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"A"}}')
    assert r1.returncode == 0
    assert {i["sk"]["S"] for i in json.loads(r1.stdout)["Items"]} == {"x", "y"}
    r2 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"B"}}')
    assert r2.returncode == 0
    assert {i["sk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"z"}
