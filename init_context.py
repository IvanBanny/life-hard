# init_context.py
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq.sdk.context.api_environment_type import ApiEnvironmentType
from config import BUNQ_API_KEY, DEVICE_DESCRIPTION, API_CONTEXT_FILE

# Create context in SANDBOX and save it
api_context = ApiContext.create(
    ApiEnvironmentType.SANDBOX,
    BUNQ_API_KEY,
    DEVICE_DESCRIPTION
)
api_context.save(API_CONTEXT_FILE)
print(f"Context saved to {API_CONTEXT_FILE}")