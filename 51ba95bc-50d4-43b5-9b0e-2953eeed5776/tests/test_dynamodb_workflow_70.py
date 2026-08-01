from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_five_tables_created_listed(cli, ddb_client, tmp_path):
    names = ["Tbl_ft_%d" % i for i in range(5)]
    for n in names:
        result = cli("dynamodb", "create-table", "--table-name", n,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    listed = ddb_client.list_tables()["TableNames"]
    for n in names:
        assert n in listed
