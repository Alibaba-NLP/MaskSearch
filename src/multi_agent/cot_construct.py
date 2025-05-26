import json
import argparse
from tqdm import tqdm
from model import call_with_messages
from web_news_get import merge_news_insert, google
from dataset import HotpotDataset
from utils import init_data, formate_data, knowledge_prompt, get_random_date, formate_check
from prompt import  Planner_Agent, Searcher_Agent, Observation_Agent
import concurrent.futures


def prediect_check(question, answer, model_response ,args):

    prompt = [{'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': f'Given the correct answer to a question, determine if the model\'s response is correct. If correct, output "correct"; if incorrect, output "incorrect". Do not include unrelated content.\nQuestion: {question}\nCorrect Answer: {answer}\nModel Response: {model_response}'}]
        
    response = call_with_messages(args.model, prompt)

    if 'incorrect' in response or 'Incorrect' in response:
        return False
    else:
        return True
            

def handle_thought_response(response, args):
    """
    return:
    next_action, current_thought
    """
    out_put = response

    if '<answer>' in out_put:
        try:
            return 'finish', out_put.split('Thought:')[1].strip()
        except:
            return 'finish', '<answer>' + out_put.split('<answer>')[1].strip()

    elif 'Thought:' in out_put:
        return 'thought', out_put.split('Thought:')[1].strip()
    
    else:
        # print(out_put)
        return 'thought', out_put
    

def construct_data(data, args):

    current_date = get_random_date()


    system_prompt = {'role': 'system', 'content': f'You are a helpful assistant. current time: {current_date}'}

    formated_data = init_data(data['query'], current_date)
    Thought_list = []  

 
    first_plan = Planner_Agent.replace('{input}', data['query'])
    
    data_prompt = [system_prompt, {'role': 'user', 'content': first_plan}]

    response = call_with_messages(args.model, data_prompt)
    action, out_data = handle_thought_response(response, args)
    Thought_list.append(out_data)
    formated_data = formate_data(formated_data, out_data, action)

    count = 0 #

    try:

        while True:
            if action == 'thought': 
                
                data_prompt = [system_prompt, {'role': 'user', 'content': Searcher_Agent.replace('{input}', Thought_list[-1])}]
                response = call_with_messages(args.model, data_prompt)
                    
                start_index = response.find("{")
                end_index = response.rfind("}") + 1
                response = response[start_index:end_index]
                
                Thought_list[-1] = Thought_list[-1] +'\n' + response
                
                action = 'rewrite'
                formated_data = formate_data(formated_data, response, action)
                queries = eval(response)['queries'] 
                if len(queries) == 0:
                    print('rewrite fail')
                    raise Exception
            
            elif action == 'rewrite': 

                news_list = [google(query) for query in queries]
                news_list = merge_news_insert(news_list, 10)

                if len(news_list) == 0:
                    print('search fail')
                    raise Exception

                observation_data = knowledge_prompt.format(content="\n\n".join(news_list))   
                action = 'observation'
                formated_data = formate_data(formated_data, observation_data, action)   
            

            elif action == 'observation':
                previous_all_thought = "\n".join(['Thought: '+ thought for thought in Thought_list])

                
                data_prompt = [system_prompt, {'role': 'user', 'content': Observation_Agent.replace('{input}', data['query']).replace('{Thought}', previous_all_thought).replace('{Observation}', observation_data)}]
                
                response = call_with_messages(args.model, data_prompt)
                action, out_data = handle_thought_response(response, args)
                Thought_list.append(out_data) 
                formated_data = formate_data(formated_data, out_data, action)

                count += 1 

            elif action == 'finish':
                formated_data['ext'] = data['ext']
                if prediect_check(data['query'], data['answer'], out_data, args):
                    formated_data['ext']['response_acc'] = True
                    return formated_data, True
                else:
                    formated_data['ext']['response_acc'] = False
                    return formated_data, True   

            elif action == 'error':
                formated_data['ext'] = data['ext']
                print('error in thought')
                return formated_data, False
            
            if count > 4:
                formated_data['ext'] = data['ext']
                data['ext']['response_acc'] = 'Max_turn'
                print('Max Thought turn')
                return formated_data, False


    except Exception as e:
        formated_data['ext'] = data['ext']
        return formated_data, False
        


if __name__ == '__main__':
    argparse = argparse.ArgumentParser()
    argparse.add_argument('--model', type=str, default='qwen-max')
    argparse.add_argument('--dataset', type=str, default='hotpot')
    argparse.add_argument('--multi_thread', action_store=True)
    argparse.add_argument('--num_threads', type=int, default=20)
    argparse.add_argument('--output_path', type=str, default='hotpot_cot.jsonl')
    argparse.add_argument('--start_index', type=int, default=0)
    argparse.add_argument('--end_index', type=int, default=20000)
    args = argparse.parse_args()


    if args.dataset == 'hotpot':
        data_test = HotpotDataset()

    
    with open(args.output_path, 'a') as f:
        if args.multi_thread == False:
            num = 0
            for item in tqdm(data_test, total=len(data_test)):
                num += 1
                if num < args.start_index:
                    continue
                if num > args.end_index:
                    break
                
                data, status = construct_data(item, args)

                if status == True:
                    status = formate_check(data['messages'])

                if status:
                    f.write(json.dumps(data, ensure_ascii= False) +'\n')
                    f.flush()
                else:
                    error_path = args.output_path.split('.jsonl')[0] + '_error.jsonl'
                    error_file = open(error_path,'a') 
                    error_file.write(json.dumps(data, ensure_ascii= False) +'\n')
                    error_file.flush()
                    error_file.close()
        
        else:
            data_test = data_test[args.start_index:args.end_index]

            print(f'start handle dataset {args.dataset}, total length is {len(data_test)}')
            end_index = min(args.end_index, len(data_test)+args.start_index)
            print(f'start index is {args.start_index}, end index is {end_index}')

            with concurrent.futures.ThreadPoolExecutor(max_workers=args.num_threads) as executor:
                results = {executor.submit(construct_data, item, args): item for item in data_test}
                
                for future in tqdm(concurrent.futures.as_completed(results),total=len(data_test)):
                    item = results[future]
                    try:
                        data, status = future.result()
                        if status == True:
                            status = formate_check(data['messages'])
                        
                        if status:
                            f.write(json.dumps(data, ensure_ascii= False) +'\n')
                            f.flush()
            
                        else:
                            error_path = args.output_path.split('.jsonl')[0] + '_error.jsonl'
                            error_file = open(error_path,'a')
                            error_file.write(json.dumps(data, ensure_ascii= False) +'\n')
                            error_file.flush()
                            error_file.close()
                    
                    except Exception as e:
                        print(f'error in thread:{item["query"]}')
                        print(e)