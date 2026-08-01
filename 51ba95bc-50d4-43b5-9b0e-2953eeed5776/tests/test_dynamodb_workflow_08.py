from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_multiple_items(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_seed1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    for i in range(5):
        result = cli("dynamodb", "put-item", "--table-name", "Tbl_seed1",
                     "--item", '{"pk":{"S":"s%d"},"n":{"N":"%d"}}' % (i, i))
        assert result.returncode == 0
    for i in range(5):
        resp = ddb_client.get_item(TableName="Tbl_seed1", Key={"pk": {"S": "s%d" % i}})
        assert from_item(resp["Item"]) == {"pk": "s%d" % i, "n": i}
