from dashscope import Generation
from http import HTTPStatus
import time
import dashscope

DASHSCOPE_API_KEY = "YOUR_API_KEY"

def call_with_messages(model, messages):
    while True:
        response = Generation.call(
            model=model,
            messages=messages,
            result_format='message',
            api_key=DASHSCOPE_API_KEY,
        )
        if response.status_code == HTTPStatus.OK:
            # print(response)
            return response.output.choices[0].message.content
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            if response.status_code == 400:
                return None
            time.sleep(1)
            continue

