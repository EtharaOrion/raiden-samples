from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multi_item_seed_readback(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "SeedTbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "SeedTbl",
                 "--item", '{"pk":{"S":"a"},"n":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "SeedTbl",
                 "--item", '{"pk":{"S":"b"},"n":{"N":"2"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "SeedTbl",
                 "--item", '{"pk":{"S":"c"},"n":{"N":"3"}}')
    assert result.returncode == 0

    got = {}
    for k in ("a", "b", "c"):
        resp = ddb_client.get_item(TableName="SeedTbl", Key={"pk": {"S": k}})
        assert "Item" in resp
        got[k] = from_item(resp["Item"])["n"]
    assert got == {"a": 1, "b": 2, "c": 3}
