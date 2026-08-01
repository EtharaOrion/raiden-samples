from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_ten_items_all_readable(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_ten1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    for i in range(10):
        result = cli("dynamodb", "put-item", "--table-name", "Tbl_ten1",
                     "--item", '{"pk":{"S":"k%d"},"idx":{"N":"%d"}}' % (i, i))
        assert result.returncode == 0
    seen = set()
    for i in range(10):
        resp = ddb_client.get_item(TableName="Tbl_ten1", Key={"pk": {"S": "k%d" % i}})
        native = from_item(resp["Item"])
        seen.add(native["idx"])
    assert seen == set(range(10))
