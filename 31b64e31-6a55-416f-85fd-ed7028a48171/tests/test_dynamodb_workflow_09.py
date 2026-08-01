from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multi_seed_get_each(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf10Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    for i in range(3):
        result = cli("dynamodb", "put-item", "--table-name", "Wf10Tbl",
                     "--item", '{"pk":{"S":"m%d"},"n":{"N":"%d"}}' % (i, i))
        assert result.returncode == 0
    for i in range(3):
        resp = ddb_client.get_item(TableName="Wf10Tbl", Key={"pk": {"S": "m%d" % i}})
        assert from_item(resp["Item"]) == {"pk": "m%d" % i, "n": i}
