from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
import bunq.sdk.model.generated.endpoint as endpoint

def endpoint_discovery():
    def find_cls(prefix: str):
        candidates = [n for n in dir(endpoint) if n.startswith(prefix)]
        if not candidates:
            raise RuntimeError(f"No endpoint class starts with '{prefix}'!")
        cls_name = candidates[0]
        print(f"→ Using {prefix} class: {cls_name}")
        return getattr(endpoint, cls_name)

    SavingsCls = find_cls("MonetaryAccountSavings")
    BankCls    = find_cls("MonetaryAccountBank")
    PaymentCls = find_cls("Payment")

    return SavingsCls, BankCls, PaymentCls

def get_budget() -> str:
    """Get user's budget string."""
    # 1. Load the Bunq API context
    SavingsCls, BankCls, PaymentCls = endpoint_discovery()

    # 2. Main bank account
    banks = BankCls.list().value
    if not banks:
        raise RuntimeError("No MonetaryAccountBank found!")
    bank = banks[0]
    bank_id = bank.id_
    bank_balance = float(bank.balance.value)
    print(f"Main account #{bank_id} has {bank_balance:.2f} EUR")

    # 3. Find or savings pot
    pots = SavingsCls.list().value
    assert pots and len(pots) > 0, "No pots found!"

    pot = pots[0]
    print(f"Found pot #{pot.id_} with {pot.balance.value} {pot.balance.currency}")

    return f"{pot.balance.value} {pot.balance.currency}"
