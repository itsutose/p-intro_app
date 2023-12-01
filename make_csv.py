import os
import pandas as pd
import json
from students_list import students_list
# from questions import questions, questions_number
from questions_created_set.questions import questions, questions_number
from pprint import pprint
# 仮の辞書を作成してキーをソートする
from collections import OrderedDict

# キーを自然順序にソートするための関数
def natural_keys(text):
    """
    自然順序ソートのためのキー関数
    """
    import re
    def atoi(text):
        return int(text) if text.isdigit() else text
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def make_csv(folder_path):

    files = os.listdir(folder_path)

    table = None
    error_list = {}
    
    

    # 学生ごとに巡る
    for k, file_name in enumerate(files):
        
        if file_name.endswith('.ipynb') == False:
            continue
        
        file_path = folder_path + '/' + file_name
        # student_id = file_name.split('@')[0]
        student_id = file_name[0:9]

        # 学生一人分の q_and_a
        q_and_a = {}
        q_and_a['student_id'] = student_id
        q_and_a['student_name'] = students_list[student_id]

        # .ipynb ファイルを読み込む
        with open(file_path, "r", encoding="utf-8")  as file:
            try:
                notebook_data = json.load(file)
            except:
                error_list[student_id] = students_list[str(student_id)]
                continue

        nums = [num for num in questions_number.values()]
        num_len = len(nums)
        if num_len != 22:
            print(f'num_len = {num_len}')
            
            
        for i in range(len(notebook_data['cells'])):

            cell = notebook_data['cells'][i]
            cell_type = cell.get("cell_type")
            metadata = cell.get("metadata")
            source = cell.get("source")
            
            # print(source)
            if cell_type == 'markdown':

                if len(source) == 0:
                    continue
                
                source_0 = source[0].replace('\n','')

                if source_0 in questions.keys():
                    # print(source)
                    
                    
                    # answer_cell = Answer_cell(questions_number[source_0])

                    # questionの下のj個までの(答えの)セルを取得する
                    for j in range(questions[source_0]):
                        next_cell = notebook_data['cells'][i+j+1]
                        next_cell_type = next_cell.get("cell_type")
                        next_metadata = next_cell.get("metadata")
                        next_source = next_cell.get("source")
                        # print(next_cell['outputs'])
                        try:
                            next_outputs = next_cell['outputs'][0]['text']
                        except:
                            next_outputs = 'Not executed.'
                        # print(next_outputs)
                        
                        # break

                        # 問題文1行のみ
                        q_and_a[questions_number[source_0]+f'_source_{j}'] = ''.join(next_source)
                        q_and_a[questions_number[source_0]+f'_output_{j}'] = ''.join(next_outputs)
                        
                        # # 取得した問題番号を削除 = 未取得のみを取得
                        # try:
                        #     nums.remove(questions_number[source_0])
                        # except Exception as e:
                            
                        #     print(f"エラーが発生しました: {type(e).__name__} - {e}")
                        #     continue
                        
                        # j個(指定のセル数を取得する際の数)が複数ある場合に，2つ目でエラーしないように
                        if questions_number[source_0] in nums:
                            nums.remove(questions_number[source_0])
                        
                        
        # print(nums)
        # q_and_a[source_0] = answer_cell.to_dict()
        # return

        # 未取得の問題を埋め合わせる
        for num in nums:
            # print(num)
            q_and_a[f'{num}_source_{j}'] = 'error'
            q_and_a[f'{num}_output_{j}'] = 'error'
            
        if nums != []:
            
            sorted_dict = {}
            sorted_dict['student_id'] = q_and_a['student_id']
            sorted_dict['student_name'] = q_and_a['student_name']
            for i in range(num_len):
                sorted_dict[f'{i+1}_source_0'] = q_and_a[f'{i+1}_source_0']
                sorted_dict[f'{i+1}_output_0'] = q_and_a[f'{i+1}_output_0']
            q_and_a = sorted_dict
            # print(q_and_a.keys())
        
        
        # tableの新規作成
        if table is None:
            table = pd.DataFrame(columns = list(q_and_a.keys()))
        

        # print(k, student_id, len(q_and_a))
        
        try:
            table.loc[k] = q_and_a.values()
        except Exception as e:
            error_info = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'student_id': student_id,
                'student_name': students_list.get(str(student_id), 'Unknown')
            }
            error_list[student_id] = error_info
            
              
            # not_contains = [q.split('_')[0] for q in q_and_a.keys() if q.split('_')[0] not in nums]
            
            pprint(f"Error for student {student_id} {students_list[str(student_id)]}: {type(e).__name__} - {e} {nums}")
            continue

    table.columns
    table.to_csv('test.csv', index = False)
    return error_list
    
if __name__ == '__main__':
    error_list = make_csv(rf'{os.getcwd()[0]}:\マイドライブ\flask_tutrial\uploaded')
 
    pprint(error_list)
    
