import json
import random

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def select_case_from_pool(json_data):
    
    for pool in json_data:
        pool_cases = pool['pool']

        case_ids = [case['id'] for case in pool_cases]
        weights = [case.get('odds', case.get('odd', 0)) for case in pool_cases]
        
        selected_case = random.choices(case_ids, weights=weights, k=1)[0]
        return selected_case

if __name__ == "__main__":
    json_file_path = 'drop_pool.json'
    json_data = load_json_file('./data/drop_pool.json')
    selected_case = select_case_from_pool(json_data)
    print(f"Selected Case: {selected_case}")
