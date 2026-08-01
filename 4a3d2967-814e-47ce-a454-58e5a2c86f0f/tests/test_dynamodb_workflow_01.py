from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_after_multi_seed(cli, ddb_client, tmp_path):
    t = "wf_query_multi_2"
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
    for sk in ["s1", "s2", "s3"]:
        ddb_client.put_item(TableName=t, Item={"pk": {"S": "p"}, "sk": {"S": sk}})
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "q"}, "sk": {"S": "s9"}})
    result = cli("dynamodb", "query", "--table-name", t,
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"p"}}')
    assert result.returncode == 0
    out = json.loads(result.stdout)
    sks = {i["sk"]["S"] for i in out["Items"]}
    assert sks == {"s1", "s2", "s3"}
    r2 = cli("dynamodb", "scan", "--table-name", t)
    assert r2.returncode == 0
    scanned = {i["sk"]["S"] for i in json.loads(r2.stdout)["Items"]}
    assert scanned == {"s1", "s2", "s3", "s9"}
