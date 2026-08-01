from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_distinct_tables_same_item_key(cli, ddb_client, tmp_path):
    for name, val in (("Tbl_dt_a", "va"), ("Tbl_dt_b", "vb")):
        result = cli("dynamodb", "create-table", "--table-name", name,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
        result = cli("dynamodb", "put-item", "--table-name", name,
                     "--item", '{"pk":{"S":"same"},"v":{"S":"%s"}}' % val)
        assert result.returncode == 0
    ra = ddb_client.get_item(TableName="Tbl_dt_a", Key={"pk": {"S": "same"}})
    rb = ddb_client.get_item(TableName="Tbl_dt_b", Key={"pk": {"S": "same"}})
    assert from_item(ra["Item"])["v"] == "va"
    assert from_item(rb["Item"])["v"] == "vb"
