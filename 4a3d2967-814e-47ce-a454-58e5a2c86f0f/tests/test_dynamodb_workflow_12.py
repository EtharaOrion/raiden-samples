from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_no_match_empty(cli, ddb_client, tmp_path):
    t = "wf_nomatch_13"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "present"}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"absent"}}')
    assert r1.returncode == 0
    assert json.loads(r1.stdout).get("Items", []) == []
    r2 = cli("dynamodb", "scan", "--table-name", t)
    assert r2.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"present"}
