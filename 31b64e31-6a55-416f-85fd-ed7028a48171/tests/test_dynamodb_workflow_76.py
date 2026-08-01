from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_bulk_put_verify_all_present(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf77Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    keys = ["a", "b", "c", "d"]
    for k in keys:
        result = cli("dynamodb", "put-item", "--table-name", "Wf77Tbl",
                     "--item", '{"pk":{"S":"%s"},"v":{"S":"%s"}}' % (k, k))
        assert result.returncode == 0
    for k in keys:
        resp = ddb_client.get_item(TableName="Wf77Tbl", Key={"pk": {"S": k}})
        assert from_item(resp["Item"]) == {"pk": k, "v": k}
