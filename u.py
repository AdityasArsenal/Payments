from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.env import Env
 
client_id = "SU2508041810254120514281"
client_secret = "c99221ef-7d77-4f9f-88da-33960804b858"
client_version = "1"  # Insert your client version here
env = Env.PRODUCTION  # Change to Env.PRODUCTION when you go live
should_publish_events = False
 
client = StandardCheckoutClient.get_instance(client_id=client_id,
                                                              client_secret=client_secret,
                                                              client_version=client_version,
                                                              env=env,
                                                              should_publish_events=should_publish_events)

merchant_order_id = '1f96396d-0d3e-43dc-911c-1331e2c025ad'
response = client.get_order_status(merchant_order_id, details=False)
 
state = response.state
print(state)