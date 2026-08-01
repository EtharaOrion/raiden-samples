from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_expr_attr_names(cli, ddb_client, tmp_path):
    t = "wf_exprnames_15"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "#p = :v",
             "--expression-attribute-names", '{"#p":"pk"}',
             "--expression-attribute-values", '{":v":{"S":"a"}}')
    assert r1.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r1.stdout)["Items"]} == {"a"}
    r2 = cli("dynamodb", "scan", "--table-name", t)
    assert r2.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"a"}
