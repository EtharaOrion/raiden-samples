from _ddb_http import to_item, from_item, to_av, from_av


def test_create_table_provisioned_billing_mode(cli, ddb_client):
    result = cli(
        "dynamodb", "create-table",
        "--table-name", "EdgeTbl",
        "--attribute-definitions", '[{"AttributeName":"id","AttributeType":"S"}]',
        "--key-schema", '[{"AttributeName":"id","KeyType":"HASH"}]',
        "--billing-mode", "PROVISIONED",
        "--provisioned-throughput", '{"ReadCapacityUnits":5,"WriteCapacityUnits":5}',
    )
    assert result.returncode == 0
    assert "EdgeTbl" in ddb_client.list_tables()["TableNames"]

    ddb_client.put_item(TableName="EdgeTbl", Item={"id": {"S": "abc"}})
    resp = ddb_client.get_item(TableName="EdgeTbl", Key={"id": {"S": "abc"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["id"]["S"] == "abc"