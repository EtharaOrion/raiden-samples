from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_between_sort(cli, ddb_client, tmp_path):
    t = "wf_between_18"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "N"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for n in ["1", "2", "3", "4", "5"]:
        ddb_client.put_item(TableName=t, Item={"pk": {"S": "p"}, "sk": {"N": n}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :p AND sk BETWEEN :lo AND :hi",
             "--expression-attribute-values", '{":p":{"S":"p"},":lo":{"N":"2"},":hi":{"N":"4"}}')
    assert r1.returncode == 0
    assert {i["sk"]["N"] for i in json.loads(r1.stdout)["Items"]} == {"2", "3", "4"}
    r2 = cli("dynamodb", "scan", "--table-name", t)
    assert r2.returncode == 0
    assert {i["sk"]["N"] for i in json.loads(r2.stdout)["Items"]} == {"1", "2", "3", "4", "5"}
