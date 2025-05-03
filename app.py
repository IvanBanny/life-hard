# app.py

import time
import logging
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
import bunq.sdk.model.generated.endpoint as endpoint
import requests
from config import API_CONTEXT_FILE

# ———————————————
# Configuration
# ———————————————
MINIMUM_TRIGGER_BALANCE = 100.0    # Only trigger LLM if savings ≥ €100
POLL_INTERVAL_SECONDS  = 30       # Check every minute

# ———————————————
# Logging & Initialization
# ———————————————
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Bunq context
api_ctx = ApiContext.restore(API_CONTEXT_FILE)
api_ctx.ensure_session_active()
BunqContext.load_api_context(api_ctx)

# ———————————————
# Discover endpoint classes
# ———————————————
def find_cls(prefix: str):
    candidates = [n for n in dir(endpoint) if n.startswith(prefix)]
    if not candidates:
        raise RuntimeError(f"No endpoint class starts with '{prefix}'!")
    return getattr(endpoint, candidates[0])

SavingsCls = find_cls("MonetaryAccountSavings")
BankCls    = find_cls("MonetaryAccountBank")
PaymentCls = find_cls("Payment")

# ———————————————
# LLM Call (local Ollama/Phi)
# ———————————————
def generate_itinerary(balance: str) -> str:
    prompt = f"I have {balance} for traveling. Create a detailed 3-day itinerary."
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma3:1b", "prompt": prompt, "stream": False},
            timeout=30
        )
        resp.raise_for_status()
        return resp.json().get("response", "[no response]")
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return "[could not generate itinerary]"

# ———————————————
# Helpers for Savings Pot
# ———————————————
def ensure_travel_pot(min_balance: float = MINIMUM_TRIGGER_BALANCE):
    """
    1. Finds your main bank account.
    2. Finds or creates a "Travel Pot" savings account.
    3. Tops it up so it has at least `min_balance`.
    Returns: (pot_id, current_balance)
    """
    # 1) Main bank account
    bank = BankCls.list().value[0]
    bank_id = bank.id_
    bank_balance = float(bank.balance.value)
    logger.info(f"Main account #{bank_id} balance: €{bank_balance:.2f}")

    # 2) Find or create pot
    pots = SavingsCls.list().value
    if pots:
        pot = pots[0]
    else:
        logger.info("No Travel Pot found → creating one.")
        resp = SavingsCls.post(
            monetary_account_savings={"currency": "EUR", "description": "Travel Pot"}
        )
        pot = resp.value[0]
    pot_id = pot.id_
    current = float(pot.balance.value)
    logger.info(f"Pot #{pot_id} balance: €{current:.2f}")

    # 3) Top up if below min_balance
    if current < min_balance:
        needed = min_balance - current
        if bank_balance < needed:
            logger.warning(f"Not enough in main account to top up (€{bank_balance:.2f} available).")
        else:
            logger.info(f"Topping up Pot #{pot_id} by €{needed:.2f}…")
            PaymentCls.create(
                amount={"value": f"{needed:.2f}", "currency": "EUR"},
                counterparty_alias=pot.alias[0],
                description="Auto top-up Travel Pot",
                monetary_account_id=bank_id
            )
            # refresh balance
            pot = [p for p in SavingsCls.list().value if p.id_ == pot_id][0]
            current = float(pot.balance.value)
            logger.info(f"Pot #{pot_id} new balance: €{current:.2f}")

    return pot_id, current

def list_savings_pots():
    """Return list of all savings pot objects."""
    return SavingsCls.list().value

# ———————————————
# Main Loop
# ———————————————
def main():
    # 1) Ensure Travel Pot exists & has at least MINIMUM_TRIGGER_BALANCE
    pot_id, last_balance = ensure_travel_pot()

    # 2) Poll forever
    while True:
        time.sleep(POLL_INTERVAL_SECONDS)
        pots = list_savings_pots()
        # find our pot again (we assume only one)
        pot = next((p for p in pots if p.id_ == pot_id), None)
        if not pot:
            logger.error(f"Pot #{pot_id} disappeared! Recreating…")
            pot_id, last_balance = ensure_travel_pot()
            continue

        new_balance = float(pot.balance.value)
        # Trigger if changed and >= threshold
        if new_balance != last_balance and new_balance >= MINIMUM_TRIGGER_BALANCE:
            logger.info(f"Balance changed! {last_balance:.2f} → {new_balance:.2f} EUR")
            itinerary = generate_itinerary(f"{new_balance:.2f} EUR")
            logger.info("🗺  Generated Itinerary:\n" + itinerary)
            last_balance = new_balance
        else:
            logger.debug(f"No trigger (balance: €{new_balance:.2f})")

if __name__ == "__main__":
    main()
