"""
Teamleader Helper functions
"""

from teamleader.exceptions import InvalidInputError


def vat_liability_to_invoice(customer_vat_liability, tariff='21', service=False):
    '''Determine invoice line vat term based on default tariff and customer VAT liability.
    '''
    tariff = str(tariff).zfill(2)

    if tariff not in ['00', '06', '12', '21']:
        raise InvalidInputError("Invalid VAT tariff.")

    if customer_vat_liability == 'intra_community_eu':
        return 'VCMD' if service else 'CM'
    elif customer_vat_liability == 'vat_liable':
        return tariff
    elif customer_vat_liability == 'outside_eu':
        return 'EX'
    elif customer_vat_liability == 'unknown':
        return tariff
    elif customer_vat_liability == 'private_person':
        return tariff
    elif customer_vat_liability == 'not_vat_liable':
        return '00'
    elif customer_vat_liability == 'contractant':
        return 'MC'
    else:
        raise InvalidInputError("Invalid customer VAT liability.")


def payment_term_to_invoice(customer_payment_term):
    '''Determine invoice line payment term based on default tariff and customer VAT settings.
    '''

    invoice_payment_term = customer_payment_term.replace('_days', 'D').replace('_end_month', 'DEM')
    if invoice_payment_term not in ['0D', '7D', '10D', '15D', '21D', '30D', '45D', '60D', '90D', '30DEM', '60DEM', '90DEM']:
        raise InvalidInputError("Invalid contents of argument customer_payment_term.")
    return invoice_payment_term
