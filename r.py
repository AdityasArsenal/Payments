from uuid import uuid4
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
from phonepe.sdk.pg.env import Env
 
client_id = "SU2508041810254120514281"
client_secret = "c99221ef-7d77-4f9f-88da-33960804b858"
client_version = "1"
env = Env.PRODUCTION
should_publish_events = False
 
client = StandardCheckoutClient.get_instance(client_id=client_id,
                                                              client_secret=client_secret,
                                                              client_version=client_version,
                                                              env=env,
                                                              should_publish_events=should_publish_events)
 


unique_order_id = str(uuid4())
ui_redirect_url = "https://gov.nonexistential.dev/"
amount = 100
meta_info = MetaInfo(udf1="silver", udf2="amount_1", udf3="payment") 
standard_pay_request = StandardCheckoutPayRequest.build_request(merchant_order_id=unique_order_id,
                                                                amount=amount,
                                                                redirect_url=ui_redirect_url,
                                                                meta_info=meta_info)
standard_pay_response = client.pay(standard_pay_request)
checkout_page_url = standard_pay_response.redirect_url

print(checkout_page_url)
print('--------------------------------')
print(standard_pay_response)
print('--------------------------------')

print(unique_order_id)