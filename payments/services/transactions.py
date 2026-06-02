from payments.models import PaymentTransaction


def create_payment_transaction(*, payer, **data):
    return PaymentTransaction.objects.create(payer=payer, **data)
