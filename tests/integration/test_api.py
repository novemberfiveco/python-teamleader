def test_get_users(api):
    users = api.get_users()
    assert isinstance(users, list)
    assert users


def test_get_contacts(api):
    contacts = api.get_contacts()
    assert list(contacts)


def test_get_companies(api):
    companies = api.get_companies()
    assert list(companies)
