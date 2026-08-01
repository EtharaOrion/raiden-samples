from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_number_set_roundtrip(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_ns1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_ns1",
                 "--item", '{"pk":{"S":"nset1"},"nums":{"NS":["1","2","3"]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_ns1", Key={"pk": {"S": "nset1"}})
    native = from_item(resp["Item"])
    assert native["pk"] == "nset1"
    assert set(native["nums"]) == {1, 2, 3}
