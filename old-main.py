# app.py

import logging
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
import bunq.sdk.model.generated.endpoint as endpoint
from config import API_CONTEXT_FILE, OPENAI_API_KEY
import requests

# ———————————————
# Logging & Initialization
# ———————————————
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load your Bunq API context (sandbox or prod)
api_context = ApiContext.restore(API_CONTEXT_FILE)
api_context.ensure_session_active()
BunqContext.load_api_context(api_context)

# ———————————————
# Runtime discovery of endpoint classes
# ———————————————
def find_cls(prefix: str):
    candidates = [n for n in dir(endpoint) if n.startswith(prefix)]
    if not candidates:
        raise RuntimeError(f"No endpoint class starts with '{prefix}'!")
    cls_name = candidates[0]
    logger.info(f"→ Using {prefix} class: {cls_name}")
    return getattr(endpoint, cls_name)

SavingsCls = find_cls("MonetaryAccountSavings")
BankCls    = find_cls("MonetaryAccountBank")
PaymentCls = find_cls("Payment")

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

def generate_itinerary(balance: str) -> str:
    """Send balance to your LLM and receive a 3-day itinerary."""
    prompt = f"I have {balance} for traveling. Create a 3-day itinerary."
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "gemma3:1b",
            "prompt": prompt,
            "stream": False
        }, timeout=60)  # Timeout after 10 seconds
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json().get('response', 'No response received')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while calling LLM API: {e}")
        return "There was an issue generating the itinerary."


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
    logger.info(f"Main account #{bank_id} has {bank_balance:.2f} EUR")

    # 2. Find or create savings pot
    pots = SavingsCls.list().value
    if pots:
        pot = pots[0]
        logger.info(f"Found pot #{pot.id_} with {pot.balance.value} {pot.balance.currency}")
    else:
        logger.info("No pot found — creating one now…")
        resp = SavingsCls.post(
            monetary_account_savings={
                "currency": "EUR",
                "description": "Travel Pot"
            }
        )
        pot = resp.value[0]
        logger.info(f"Created pot #{pot.id_} (balance {pot.balance.value} EUR)")

    # 3. Top up to reach target_balance
    current = float(pot.balance.value)
    if current >= target_balance:
        logger.info(f"Pot already has ≥{target_balance:.2f} EUR; no transfer needed.")
    else:
        needed = target_balance - current
        if bank_balance < needed:
            raise RuntimeError(f"Insufficient funds in main account ({bank_balance:.2f} EUR) to top up {needed:.2f} EUR.")
        logger.info(f"Transferring {needed:.2f} EUR into pot #{pot.id_}…")
        PaymentCls.create(
            amount={"value": f"{needed:.2f}", "currency": "EUR"},
            counterparty_alias=pot.alias[0],
            description="Top-up Travel Pot",
            monetary_account_id=bank_id
        )
        logger.info("Transfer complete.")

        # Refresh pot object so it has updated balance
        pot = [p for p in SavingsCls.list().value if p.id_ == pot.id_][0]
        logger.info(f"New pot balance: {pot.balance.value} {pot.balance.currency}")

    return pot

# ———————————————
# Main entrypoint
# ———————————————
def main():
    # 1. Ensure travel pot ends up with €500
    pot = ensure_travel_pot(target_balance=500.0)

    # 2. Invoke LLM with the final balance
    balance_str = f"{pot.balance.value} {pot.balance.currency}"
    logger.info(f"Generating itinerary for {balance_str}…")
    itinerary = generate_itinerary(balance_str)
    logger.info("Here’s your itinerary:\n" + itinerary)

if __name__ == "__main__":
    main()
