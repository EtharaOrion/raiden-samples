from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_many_items_same_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf30Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    for i in range(5):
        result = cli("dynamodb", "put-item", "--table-name", "Wf30Tbl",
                     "--item", '{"pk":{"S":"item%d"},"idx":{"N":"%d"}}' % (i, i))
        assert result.returncode == 0
    for i in range(5):
        resp = ddb_client.get_item(TableName="Wf30Tbl", Key={"pk": {"S": "item%d" % i}})
        assert resp["Item"]["idx"]["N"] == str(i)
