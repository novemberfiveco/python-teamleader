"""
Teamleader API Wrapper class
"""

import requests
import logging
import pycountry
import datetime
import time

from teamleader.exceptions import *


logging.basicConfig(level='ERROR')
log = logging.getLogger('teamleader.api')

base_url = "https://www.teamleader.be/api/{0}.php"
amount = 100


class Teamleader(object):

    _valid_payment_terms = ['0D', '7D', '10D', '15D', '21D', '30D', '45D', '60D', '90D', '30DEM', '60DEM', '90DEM']

    def __init__(self, api_group, api_secret):
        log.debug("Initializing Teamleader with group {0} and secret {1}".format(api_group, api_secret))
        self.group = api_group
        self.secret = api_secret

    def _request(self, endpoint, data=None):
        """Internal method for making a request to a Teamleader endpoint.
        """
        log.debug("Making a request to the Teamleader API endpoint {0}".format(endpoint))
        data = data or {}
        data['api_group'] = self.group
        data['api_secret'] = self.secret

        r = requests.post(base_url.format(endpoint), data=data)
        response = r.json()

        if r.status_code == requests.codes.unauthorized:
            raise TeamleaderUnauthorizedError(message=response['reason'], api_response=r)

        if r.status_code == 505:
            raise TeamleaderRateLimitExceededError(message=response['reason'], api_response=r)

        if r.status_code == requests.codes.bad_request:
            raise TeamleaderBadRequestError(message=response['reason'], api_response=r)

        if r.status_code == requests.codes.ok:
            return r.json()

        raise TeamleaderUnknownAPIError(message=response['reason'], api_response=r)

    @staticmethod
    def _validate_type(arg, t):
        if arg and not isinstance(arg, t):
            raise InvalidInputError('Invalid argument: ' + repr(arg))

        return arg or t()

    @staticmethod
    def _convert_custom_fields(data):
        for custom_field_id, custom_field_value in data.pop('custom_fields').items():
            data['custom_field_' + str(custom_field_id)] = custom_field_value

    @staticmethod
    def _clean_input_to_dict(data):
        for key in data.keys():
            if data[key] is None:
                del data[key]
            elif isinstance(data[key], bool):
                data[key] = int(data[key])
        return data

    def get_users(self, show_inactive_users=False):
        """Getting all users.

        Args:
            show_inactive_users: 0/1 If this flag is set to 1, Teamleader will
                return also return inactive users

        Returns:
            List of dicts containing ID's and real names of all users.
        """

        return self._request('getUsers', {'show_inactive_users': int(show_inactive_users)})

    def get_departments(self):
        """Getting all departments.

        Returns:
            List of dicts containing ID's and names of all departments in your account.
        """

        return self._request('getDepartments')

    def get_tags(self):
        """Getting all tags.

        Returns:
            List of dicts containing ID's and names of all tags in your account.
        """

        return self._request('getTags')

    def get_segments(self, object_type):
        """Getting segments.

        Args:
            object_type: pick one option - crm_companies, crm_contacts, crm_todos,
                crm_callbacks, crm_meetings, inv_invoices, inv_creditnotes, pro_projects,
                sale_sales or ticket_tickets.

        Returns:
            List of dicts containing ID's and names of relevant segments in your account.
        """

        if object_type not in ['crm_companies', 'crm_contacts', 'crm_todos', 'crm_callbacks', 'crm_meetings', 'inv_invoices', 'inv_creditnotes', 'pro_projects', 'sale_sales', 'ticket_tickets']:
            raise InvalidInputError("Invalid contents of object_type.")

        return self._request('getSegments', {'object_type': object_type})

    def add_contact(self, forename, surname, email, salutation=None, telephone=None, gsm=None,
            website=None, country=None, zipcode=None, city=None, street=None, number=None,
            language=None, gender=None, date_of_birth=None, description=None, newsletter=None, tags=None,
            automerge_by_name=False, automerge_by_email=False, custom_fields=None, tracking=None,
            tracking_long=None):
        """Adding a contact to Teamleader.

        Args:
            forename: string
            surname: string
            email: string
            salutation: string
            telephone: string
            gsm: string
            website: string
            country: string: country code according to ISO 3166-1 alpha-2. For Belgium: "BE"
            zipcode: string
            city: string
            street: string
            number: string
            language: string: language code according to ISO 639-1. For Dutch: "NL"
            gender: M/F/U
            date_of_birth: datetime.date object
            description: background information on the contact
            newsletter: True/False
            tags: list of tags. Existing tags will be reused, other tags will be
                automatically created for you.
            automerge_by_name: True/False If this flag is set to True, Teamleader will merge this
                info into an existing contact with the same forename and surname, if it finds any.
            automerge_by_email: True/False If this flag is set to True, Teamleader will merge this
                info into an existing contact with the same email address, if it finds any.
            custom_fields: dict with keys the IDs of your custom fields and values the value to be set.
            tracking: title of the activity
            tracking_long: description of the activity

        Returns:
            ID of the contact that was added.
        """

        # get all arguments
        data = self._clean_input_to_dict(locals())

        # argument validation
        if gender is not None and gender not in ['M', 'F', 'U']:
            raise InvalidInputError("Invalid contents of argument gender.")

        tags = self._validate_type(tags, list)
        custom_fields = self._validate_type(custom_fields, dict)

        if country is not None:
            try:
                pycountry.countries.get(alpha2=country.upper())
            except:
                raise InvalidInputError("Invalid contents of argument country.")

        if language is not None:
            try:
                pycountry.languages.get(iso639_1_code=language.lower())
            except:
                raise InvalidInputError("Invalid contents of argument language.")

        if date_of_birth is not None and type(date_of_birth) != datetime.date:
            raise InvalidInputError("Invalid contents of argument date_of_birth.")

        # convert data elements that need conversion
        data['add_tag_by_string'] = ','.join(data.pop('tags'))
        self._convert_custom_fields(data)

        if date_of_birth is not None:
            data['dob'] = time.mktime(data.pop('date_of_birth').timetuple())

        if newsletter is not None:
            data['newsletter'] = int(newsletter)

        data['automerge_by_name'] = int(automerge_by_name)
        data['automerge_by_email'] = int(automerge_by_email)

        return self._request('addContact', data)

    def update_contact(self, contact_id, track_changes=True,
            forename=None, surname=None, email=None, telephone=None, gsm=None,
            website=None, country=None, zipcode=None, city=None, street=None, number=None,
            language=None, gender=None, date_of_birth=None, description=None,
            tags=None, del_tags=None, custom_fields=None, linked_company_ids=None):
        """Updating contact information.

        Args:
            contact_id: integer: ID of the contact
            track_changes: True/False: if set to True, all changes are logged and visible to users
                in the web-interfae
            forename: string
            surname: string
            email: string
            telephone: string
            gsm: string
            website: string
            country: string: country code according to ISO 3166-1 alpha-2. For Belgium: "BE"
            zipcode: string
            city: string
            street: string
            number: string
            language: string: language code according to ISO 639-1. For Dutch: "NL"
            gender: M/F/U
            date_of_birth: datetime.date object
            description: background information on the contact
            newsletter: True/False
            tags: list of tags to add. Existing tags will be reused, other tags will be
                automatically created for you.
            del_tags: list of tags to remove.
            custom_fields: dict with keys the IDs of your custom fields and values the value to be set.
        """

        # get all arguments
        data = self._clean_input_to_dict(locals())

        # argument validation
        if gender is not None and gender not in ['M', 'F', 'U']:
            raise InvalidInputError("Invalid contents of argument gender.")

        tags = self._validate_type(tags, list)
        del_tags = self._validate_type(del_tags, list)
        custom_fields = self._validate_type(custom_fields, dict)

        if country is not None:
            try:
                pycountry.countries.get(alpha2=country.upper())
            except:
                raise InvalidInputError("Invalid contents of argument country.")

        if language is not None:
            try:
                pycountry.languages.get(iso639_1_code=language.lower())
            except:
                raise InvalidInputError("Invalid contents of argument language.")

        if date_of_birth is not None and type(date_of_birth) != datetime.date:
            raise InvalidInputError("Invalid contents of argument date_of_birth.")

        # convert data elements that need conversion
        data['add_tag_by_string'] = ','.join(data.pop('tags'))
        data['remove_tag_by_string'] = ','.join(data.pop('del_tags'))

        for custom_field_id, custom_field_value in data.pop('custom_fields').items():
            data['custom_field_' + str(custom_field_id)] = custom_field_value

        if date_of_birth is not None:
            data['dob'] = time.mktime(data.pop('date_of_birth').timetuple())

        self._request('updateContact', data)

    def delete_contact(self, contact_id):
        """Deleting a contact.

        Args:
            contact_id: integer: ID of the contact
        """

        self._request('deleteContact', {'contact_id': contact_id})

    def link_contact_company(self, contact_id, company_id, function=None):
        """Deleting a contact.

        Args:
            contact_id: integer: ID of the contact
            company_id: integer: ID of the company
            function: string: the job title the contact holds at the company (eg: HR manager)
        """

        self._request('linkContactToCompany', {'contact_id': contact_id, 'company_id': company_id, 'mode': 'link', 'function': function})

    def unlink_contact_company(self, contact_id, company_id):
        """Deleting a contact.

        Args:
            contact_id: integer: ID of the contact
            company_id: integer: ID of the company
        """

        self._request('linkContactToCompany', {'contact_id': contact_id, 'company_id': company_id, 'mode': 'unlink'})

    def get_contacts(self, query=None, modified_since=None, filter_by_tag=None, segment_id=None, selected_customfields=None):
        """Searching Teamleader contacts.

        Args:
            query: string: a search string. Teamleader will try to match each part of the
                string to the forename, surname, company name and email address.
            modified_since: integer: Unix timestamp. Teamleader will only return contacts that
                have been added or modified since that timestamp.
            filter_by_tag: string: Company tag. Teamleader will only return companies that
                have the tag.
            segment_id: integer: The ID of a segment created for contacts. Teamleader will
                only return contacts that have been filtered out by the segment settings.
            selected_customfields: list of the IDs of the custom fields you wish to select
                (max 10).

        Returns:
            Iterator over the contacts found.
        """

        data = {}
        if query is not None:
            data['searchby'] = query
        if modified_since is not None:
            data['modifiedsince'] = modified_since
        if filter_by_tag is not None:
            data['filter_by_tag'] = filter_by_tag
        if segment_id is not None:
            data['segment_id'] = segment_id
        selected_customfields = self._validate_type(selected_customfields, list)
        if selected_customfields:
            data['selected_customfields'] = ','.join([str(x) for x in selected_customfields])

        there_are_more_pages = True
        pageno = 0
        while there_are_more_pages:
            page_data = {'amount': amount, 'pageno': pageno}
            page_data.update(data)
            contacts = self._request('getContacts', page_data)
            there_are_more_pages = (len(contacts) == amount)
            for contact in contacts:
                yield contact
            pageno += 1

    def get_contact(self, contact_id):
        """Fetching contact information.

        Args:
            contact_id: integer: ID of the contact

        Returns:
            Dictionary with contact details.
        """

        return self._request('getContact', {'contact_id': contact_id})

    def get_contacts_by_company(self, company_id):
        """Getting all contacts related to a company.

        Args:
            company_id: integer: the ID of the company

        Returns:
            Iterator over the contacts found.
        """

        contacts = self._request('getContactsByCompany', {'company_id': company_id})
        for contact in contacts:
            yield contact

    def add_company(self, name, email=None, vat_code=None, telephone=None, country=None, zipcode=None,
            city=None, street=None, number=None, website=None, description=None, account_manager_id=None,
            local_business_number=None, business_type=None, language=None, tags=None, payment_term=None,
            automerge_by_name=False, automerge_by_email=False, automerge_by_vat_code=False, custom_fields=None):
        """Adding a company to Teamleader.

        Args:
            name: string
            email: string
            vat_code: string
            telephone: string
            country: string: country code according to ISO 3166-1 alpha-2. For Belgium: "BE"
            zipcode: string
            city: string
            street: string
            number: string
            website: string
            description: string
            account_manager_id: ID: id of the user.
            local_business_number: string containing the local business number (KVK in the Netherlands)
            business_type: string containing the company type (eg NV, BVBA,..)
            language: string: language code according to ISO 639-1. For Dutch: "NL"
            tags: list of tags. Existing tags will be reused, other tags will be automatically created
                for you.
            payment_term: 0D / 7D / 10D / 15D / 21D / 30D / 45D / 60D / 90D / 30DEM / 60DEM / 90DEM. Default: 30D
            automerge_by_name: True/False If this flag is set to True, Teamleader will merge this info
                into an existing company with the same name, if it finds any.
            automerge_by_email: True/False If this flag is set to True, Teamleader will merge this info
                into an existing company with the same email address, if it finds any.
            automerge_by_vat_code: True/False If this flag is set to True, Teamleader will merge this info
                into an existing company with the same VAT code, if it finds any.
            custom_fields: dict with keys the IDs of your custom fields and values the value to be set.

        Returns:
            ID of the contact that was added.
        """

        # get all arguments
        data = self._clean_input_to_dict(locals())

        # argument validation
        tags = self._validate_type(tags, list)
        custom_fields = self._validate_type(custom_fields, dict)

        if country is not None:
            try:
                pycountry.countries.get(alpha2=country.upper())
            except:
                raise InvalidInputError("Invalid contents of argument country.")

        if language is not None:
            try:
                pycountry.languages.get(iso639_1_code=language.lower())
            except:
                raise InvalidInputError("Invalid contents of argument language.")

        if payment_term is not None:
            if payment_term not in self._valid_payment_terms:
                raise InvalidInputError("Invalid contents of argument payment_term.")

        # convert data elements that need conversion
        data['add_tag_by_string'] = ','.join(data.pop('tags'))

        for custom_field_id, custom_field_value in data.pop('custom_fields').items():
            data['custom_field_' + str(custom_field_id)] = custom_field_value

        data['automerge_by_name'] = int(automerge_by_name)
        data['automerge_by_email'] = int(automerge_by_email)
        data['automerge_by_vat_code'] = int(automerge_by_vat_code)

        return self._request('addCompany', data)

    def update_company(self, company_id, track_changes=True,
            name=None, email=None, vat_code=None, telephone=None, country=None, zipcode=None,
            city=None, street=None, number=None, website=None, description=None, account_manager_id=None,
            local_business_number=None, business_type=None, language=None, payment_term=None,
            tags=None, del_tags=None, custom_fields=None):
        """Updating company information.

        Args:
            company_id: integer: ID of the company
            track_changes: True/False: if set to True, all changes are logged and visible to users
                in the web-interface
            name: string
            email: string
            vat_code: string
            telephone: string
            country: string: country code according to ISO 3166-1 alpha-2. For Belgium: "BE"
            zipcode: string
            city: string
            street: string
            number: string
            website: string
            description: string
            account_manager_id: ID: id of the user.
            local_business_number: string containing the local business number (KVK in the Netherlands)
            business_type: string containing the company type (eg NV, BVBA,..)
            language: string: language code according to ISO 639-1. For Dutch: "NL"
            payment_term: 0D / 7D / 10D / 15D / 21D / 30D / 45D / 60D / 90D / 30DEM / 60DEM / 90DEM. Default: 30D
            tags: list of tags. Existing tags will be reused, other tags will be automatically created
                for you.
            del_tags: list of tags to remove.
            custom_fields: dict with keys the IDs of your custom fields and values the value to be set.
        """

        # get all arguments
        data = self._clean_input_to_dict(locals())

        # argument validation
        tags = self._validate_type(tags, list)
        del_tags = self._validate_type(del_tags, list)
        custom_fields = self._validate_type(custom_fields, dict)

        if country is not None:
            try:
                pycountry.countries.get(alpha2=country.upper())
            except:
                raise InvalidInputError("Invalid contents of argument country.")

        if language is not None:
            try:
                pycountry.languages.get(iso639_1_code=language.lower())
            except:
                raise InvalidInputError("Invalid contents of argument language.")

        if payment_term is not None:
            if payment_term not in self._valid_payment_terms:
                raise InvalidInputError("Invalid contents of argument payment_term.")

        # convert data elements that need conversion
        data['add_tag_by_string'] = ','.join(data.pop('tags'))
        data['remove_tag_by_string'] = ','.join(data.pop('del_tags'))

        for custom_field_id, custom_field_value in data.pop('custom_fields').items():
            data['custom_field_' + str(custom_field_id)] = custom_field_value

        self._request('updateCompany', data)

    def delete_company(self, company_id):
        """Deleting a company.

        Args:
            company_id: integer: ID of the company
        """

        self._request('deleteCompany', {'company_id': company_id})

    def get_companies(self, query=None, modified_since=None, filter_by_tag=None, segment_id=None, selected_customfields=None):
        """Searching Teamleader companies.

        Args:
            query: string: a search string. Teamleader will try to match each part of the
                string to the company name and email address.
            modified_since: integer: Unix timestamp. Teamleader will only return companies that
                have been added or modified since that timestamp.
            filter_by_tag: string: Company tag. Teamleader will only return companies that
                have the tag.
            segment_id: integer: The ID of a segment created for companies. Teamleader will
                only return companies that have been filtered out by the segment settings.
            selected_customfields: list of the IDs of the custom fields you wish to select
                (max 10).

        Returns:
            Iterator over the companies found.
        """

        data = {}
        if query is not None:
            data['searchby'] = query
        if modified_since is not None:
            data['modifiedsince'] = modified_since
        if filter_by_tag is not None:
            data['filter_by_tag'] = filter_by_tag
        if segment_id is not None:
            data['segment_id'] = segment_id
        selected_customfields = self._validate_type(selected_customfields, list)
        if selected_customfields:
            data['selected_customfields'] = ','.join([str(x) for x in selected_customfields])

        there_are_more_pages = True
        pageno = 0
        while there_are_more_pages:
            page_data = {'amount': amount, 'pageno': pageno}
            page_data.update(data)
            companies = self._request('getCompanies', page_data)
            there_are_more_pages = (len(companies) == amount)
            for company in companies:
                yield company
            pageno += 1

    def get_company(self, company_id):
        """Fetching company information.

        Args:
            company_id: integer: ID of the company

        Returns:
            Dictionary with company details.
        """

        return self._request('getCompany', {'company_id': company_id})

    def get_business_types(self, country):
        """Getting all possible business types for a country.

        Args:
            country: country code according to ISO 3166-1 alpha-2. For Belgium: "BE"

        Returns:
            List of names of business types (legal structures) a company can have
            within a certain country.
        """

        if country is not None:
            try:
                pycountry.countries.get(alpha2=country.upper())
            except:
                raise InvalidInputError("Invalid contents of argument country.")

        return [d['name'] for d in self._request('getBusinessTypes', {'country': country})]

    def add_invoice(self, sys_department_id, contact_id=None, company_id=None, for_attention_of=None,
            payment_term=None, invoice_lines=None, draft_invoice=False, layout_id=None, date=None,
            po_number=None, direct_debit=False, comments=None, force_set_number=None, custom_fields=None):
        """Adding an Invoice to Teamleader.

        Args:
            sys_department_id: ID of the department the invoice will be added to
            contact_id: integer: ID of the contact for which this invoice is intended.
            company_id: integer: ID of the company for which this invoice is intended.
            invoice_lines: list of dictionaries, each containing the following keys:
                description: string
                price: decimal
                amount: decimal
                vat: 00 / 06 / 12 / 21 / CM / EX / MC / VCMD: the vat tariff for this line
                product_id: id of the product (optional)
                account: id of the bookkeeping account (optional)
                subtitle: string (optional)
            for_attention_of: string
            payment_term: 0D / 7D / 10D / 15D / 21D / 30D / 45D / 60D / 90D / 30DEM / 60DEM / 90DEM
            draft_invoice: True/False: set to True to insert this invoice as a draft. (default: False)
            layout_id: ID of the custom layout you wish to use for this invoice
            date: datetime.date object: the date of the invoice. (default: today)
            po_number: string
            direct_debit: True/False: set to True to enable direct debit
            comments: string
            force_set_number: integer: force invoice number to the given integer
            custom_fields: dict with keys the IDs of your custom fields and values the value to be set

        Returns:
            ID of the invoice that was added.
        """

        # get all arguments
        data = self._clean_input_to_dict(locals())

        # argument validation
        if contact_id is None and company_id is None:
            raise InvalidInputError("One of contact_id or company_id is required.")

        if contact_id is not None and company_id is not None:
            raise InvalidInputError("Only one of contact_id or company_id is can be set.")

        if payment_term is not None:
            if payment_term not in self._valid_payment_terms:
                raise InvalidInputError("Invalid contents of argument payment_term.")

        invoice_lines = self._validate_type(invoice_lines, list)
        for line in invoice_lines:
            if not {'description', 'amount', 'vat', 'price'}.issubset(line.keys()):
                raise InvalidInputError("Fields description, amount, vat and price are required for each line.")

            if line['vat'] not in ['00', '06', '12', '21', 'CM', 'EX', 'MC', 'VCMD']:
                raise InvalidInputError("Invalid contents of argument vat.")

        if date is not None and type(date) != datetime.date:
            raise InvalidInputError("Invalid contents of argument date.")

        custom_fields = self._validate_type(custom_fields, dict)

        # convert data elements that need conversion
        self._convert_custom_fields(data)

        if contact_id is not None:
            data['contact_or_company'] = 'contact'
            data['contact_or_company_id'] = data.pop('contact_id')
        else:
            data['contact_or_company'] = 'company'
            data['contact_or_company_id'] = data.pop('company_id')

        i = 1
        for line in invoice_lines:
            data['description_' + str(i)] = line['description']
            data['price_' + str(i)] = line['price']
            data['amount_' + str(i)] = line['amount']
            data['vat_' + str(i)] = line['vat']

            if 'product_id' in data:
                data['product_id_' + str(i)] = line['product_id']
            if 'account' in data:
                data['account_' + str(i)] = line['account']
            if 'subtitle' in data:
                data['subtitle_' + str(i)] = line['subtitle']

            i += 1

        del(data['invoice_lines'])

        if date is not None:
            data['date'] = data.pop('date').strftime('%d/%m/%Y')

        return self._request('addInvoice', data)

    def add_creditnote(self):
        pass

    def update_invoice_payment_status(self):
        pass

    def book_draft_invoice(self):
        pass

    def update_invoice(self):
        pass

    def update_invoice_comment(self):
        pass

    def delete_invoice(self):
        pass

    def get_invoices(self):
        pass

    def get_creditnotes(self):
        pass

    def get_invoice(self):
        pass

    def get_creditnote(self):
        pass
