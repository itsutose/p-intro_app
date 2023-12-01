import re
from pprint import pprint 
import pandas as pd
from collections import defaultdict


def remove_trailing_spaces(code: str) -> str:
    lines = code.split('\n')
    stripped_lines = [line.rstrip() for line in lines]
    return '\n'.join(stripped_lines)

def remove_escaped_quotes(code_str):
    return code_str.replace(r"\'", "'")


# 各行に対して#から\nの直前までの文字列を除去する関数
def remove_comment(row):

    # #のコメントの行を最後の改行手前まで削除
    row = re.sub(r'#.*?(?=\n)', '\n', row)

    # \n から \nまでのスペース，タブ，改行，キャリッジリターンを消去
    row = re.sub(r'\n[\s]*\n', '\n', row)

    # = の前後の空白を1つのスペースに統一
    row = re.sub(r'\s*=\s*', '=', row)
    
    # , の前後の空白を1つのスペースに統一
    row = re.sub(r'\s*,\s*', ', ', row)

    # * の前後を空白なしに統一
    row = re.sub(r'\s*[\*\+]\s*', '*', row)

    # * の前後を空白なしに統一
    row = re.sub(r'\s*\*\s*', '*', row)

    # % の前後を空白なしに統一
    row = re.sub(r'\s*\%\s*', '%', row)


    # 行の末尾の空白やタブを取り除く
    # row = row.rstrip()
    row = remove_trailing_spaces(row)

    # row = row.replace("\\'","\'")
    # row = remove_escaped_quotes(row)

    return row

def extract_nunber_source_output(df, number):

    def group_columns(column_list):
        # Create a defaultdict to hold groups of columns
        grouped_columns = defaultdict(list)

        # Regular expression pattern to match the columns
        pattern = re.compile(r'(\d+)_(source|output)_(\d+)')

        for col in column_list:
            match = pattern.match(col)
            if match:
                # Extracting group components from the column name
                number, source_or_answer, index = match.groups()
                key = f"{number}_{source_or_answer}"
                grouped_columns[key].append(col)
        
        # Sort each group by the index
        for key in grouped_columns:
            grouped_columns[key].sort(key=lambda x: int(pattern.match(x).group(3)))

        return grouped_columns

    sources_outputs = []
    grouped_cols = group_columns(df.columns)
    for source, output in zip(grouped_cols[f'{number}_source'], grouped_cols[f'{number}_output']):
        sources_outputs.append(source)
        sources_outputs.append(output)

    return df[['student_id', 'student_name']+sources_outputs]



"""
uniqueの取得の仕方についてはchatGPTを用いるなり，向上の余地がある．
"""
# def improved_add_unique_program_num(series, column_name):
#     # Apply the remove_comment function and get unique values
#     unique_codes = series.apply(remove_comment).unique()

#     # Create an empty list to store the index mapping
#     mapping = []

#     # For each original code, find the matching index from unique codes
#     for original_code in series:
#         transformed_code = remove_comment(original_code)
#         index = list(unique_codes).index(transformed_code)
#         mapping.append(index)

#     # Convert series to dataframe
#     df = series.to_frame()
#     df[column_name +'_unique'] = mapping

#     return df

def improved_add_unique_program_num(series, column_name):
    # Apply the remove_comment function and count the occurrences of each unique code
    transformed_series = series.apply(remove_comment)
    freq = transformed_series.value_counts()

    # Sort unique codes by their frequencies in descending order
    sorted_unique_codes = freq.index.tolist()

    # Create a dictionary to map each unique code to its rank
    code_to_rank = {code: i for i, code in enumerate(sorted_unique_codes, start=1)}

    # Map each code in the series to its rank
    mapping = transformed_series.map(code_to_rank).tolist()

    # Convert series to dataframe
    df = series.to_frame()
    df[column_name + '_unique'] = mapping

    return df


def extract_df(df, number):

    tdf = extract_nunber_source_output(df, number)

    result_df = tdf.iloc[:,:2]
    # for column in tdf.columns[2:]:
    #     column
        
    for i in range(len(tdf.columns[2:])):
        # print(i+2)
        result_df = pd.concat([result_df, improved_add_unique_program_num(tdf.iloc[:,i+2], tdf.iloc[:,i+2].name)],axis=1)
        
    return result_df

if __name__ == '__main__':
    import os
    df = pd.read_csv(rf'{os.getcwd()[0]}:\マイドライブ\TA\p-intro\extract\test.csv')
    tdf = extract_df(df, 3)
    tdf