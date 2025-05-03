"""This script runs before the flask app starts."""

from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
import bunq.sdk.model.generated.endpoint as endpoint
from config import API_CONTEXT_FILE

from src.bunq_utils import endpoint_discovery

# Load the Bunq API context (sandbox or prod)
api_context = ApiContext.restore(API_CONTEXT_FILE)
api_context.ensure_session_active()
BunqContext.load_api_context(api_context)

# ———————————————
# Runtime discovery of endpoint classes
# ———————————————
SavingsCls, BankCls, PaymentCls = endpoint_discovery()

# ———————————————
# Core functions
# ———————————————
# def generate_itinerary(balance: str) -> str:
#     """Send balance to your LLM and receive a 3-day itinerary."""
#     prompt = f"I have {balance} for traveling. Create a 3-day itinerary."
#     resp = openai.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return resp.choices[0].message.content

def ensure_travel_pot(target_balance: float = 500.0):
    """
    1. Find your main bank account.
    2. Find or create a savings pot.
    3. Transfer exactly the amount needed so the pot has `target_balance`.
    Returns the pot object.
    """
    # 1. Main bank account
    banks = BankCls.list().value
    if not banks:
        raise RuntimeError("No MonetaryAccountBank found!")
    bank = banks[0]
    bank_id = bank.id_
    bank_balance = float(bank.balance.value)
    print(f"Main account #{bank_id} has {bank_balance:.2f} EUR")

    # 2. Find or create savings pot
    pots = SavingsCls.list().value
    if pots:
        pot = pots[0]
        print(f"Found pot #{pot.id_} with {pot.balance.value} {pot.balance.currency}")
    else:
        print("No pot found — creating one now…")
        resp = SavingsCls.post(
            monetary_account_savings={
                "currency": "EUR",
                "description": "Travel Pot"
            }
        )
        pot = resp.value[0]
        print(f"Created pot #{pot.id_} (balance {pot.balance.value} EUR)")

    # 3. Top up to reach target_balance
    current = float(pot.balance.value)
    if current >= target_balance:
        print(f"Pot already has ≥{target_balance:.2f} EUR; no transfer needed.")
    else:
        needed = target_balance - current
        if bank_balance < needed:
            raise RuntimeError(f"Insufficient funds in main account ({bank_balance:.2f} EUR) to top up {needed:.2f} EUR.")
        print(f"Transferring {needed:.2f} EUR into pot #{pot.id_}…")
        PaymentCls.create(
            amount={"value": f"{needed:.2f}", "currency": "EUR"},
            counterparty_alias=pot.alias[0],
            description="Top-up Travel Pot",
            monetary_account_id=bank_id
        )
        print("Transfer complete.")

        # Refresh pot object so it has updated balance
        pot = [p for p in SavingsCls.list().value if p.id_ == pot.id_][0]
        print(f"New pot balance: {pot.balance.value} {pot.balance.currency}")

    return pot

# ———————————————
# Bunq stuff setup
# ———————————————
if __name__ == "__main__":
    # 1. Ensure travel pot ends up with €500
    pot = ensure_travel_pot(target_balance=500.0)
    # balance_str = f"{pot.balance.value} {pot.balance.currency}"
