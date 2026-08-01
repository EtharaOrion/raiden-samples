from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_select_count(cli, ddb_client, tmp_path):
    t = "wf_qcount_32"
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
    for s in ["a", "b", "c"]:
        ddb_client.put_item(TableName=t, Item={"pk": {"S": "p"}, "sk": {"S": s}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"p"}}',
             "--select", "COUNT")
    assert r1.returncode == 0
    assert json.loads(r1.stdout)["Count"] == 3
    r2 = cli("dynamodb", "scan", "--table-name", t)
    assert r2.returncode == 0
    assert {i["sk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"a", "b", "c"}
