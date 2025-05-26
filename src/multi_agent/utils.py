
import random
from datetime import datetime, timedelta


def get_random_date():
   
    start_date = datetime.now() - timedelta(days=30)
    
    random_date = start_date + timedelta(days=random.randint(0, 30))
    
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    formatted_date = random_date.strftime("%Y year %m month %d day，") + weekdays[random_date.weekday()]
    return formatted_date



knowledge_prompt = """<information>：

{content}
</information>
"""

def init_data(query, date):

    data = {
    "type": "chatml",
    "messages": [
        {
            "role": "system",
            "content": f"You are a helpful assistant.\n\n current time：{date}"
        },
        {
            "content": query,
            "role": "user"
        }
    ],
    "functions": [
    {
        "name_for_human": "web_search",
        "name_for_model": "web_search",
        "description_for_model": "Utilize the web search engine to retrieve relevant information based on multiple queries.",
        "parameters": {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "The search query."
                    },
                    "description": "The list of search queries."
                }
            },
            "required": [
                "queries"
            ]
        }
    }
    ]
    }
    return data

def formate_data(data, extra_data, action):
    action = action.lower()
    if action == "thought":
        data["messages"].append({
            "role": "assistant",
            "content": extra_data,
            "function_call": {
                "name": "web_search",
                "arguments": None
            }
        })
    elif action == "rewrite":
        data["messages"][-1]["function_call"]["arguments"] = extra_data

    elif action == "observation":
        data["messages"].append({
            "role": "function",
            "name": "web_search",
            "content": extra_data
        })

    elif action == "finish":
        data["messages"].append({
            "content": extra_data,
            "finish_reason": "stop",
            "function_call": {
            },
            "response_role": "assistant",
            "role": "assistant"
        })
    
    return data


def formate_check(messages):
   
    if_continue = False
    
    for message in messages:
        
        if 'function_call' in message and 'finish_reason' not in message:
            if message['function_call']['arguments'] is None:
                if_continue = True
        
        
        if 'Act: {' in message['content'] or 'Observation:' in message['content']:
            if_continue = True
    
    return not if_continue