from datetime import datetime
import json
import re
import os
from sqlite3 import IntegrityError
from bs4 import BeautifulSoup
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, jsonify, render_template, Flask, request, render_template_string, redirect, url_for
import pytz
from unique_program import extract_df
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import relationship
from ast import literal_eval
from werkzeug.utils import secure_filename
from students_list import students_list as STUDENT_LIST
from lesson_number import lesson_numbers as LESSON_NUMBERS
from make_csv import make_csv
from questions_created_set.questions import questions_number as QUESTIONS_NUMBER, questions_name_to_number as QUESTIONS_NAME
from sqlalchemy import inspect
import subprocess
from pprint import pprint

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)

# # 何回目のレッスン
# NOW_LESSON_NUMBER = None
NOW_LESSON_NUMBER = None

# # データベースのパス
# DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, "instance", "Lesson04_5.db")}'
DATABASE_URL = None

# # アップロードされたファイルを保存するフォルダを指定
# UPLOADED_FOLDER_PATH = os.path.join(BASE_DIR, "uploaded")
UPLOADED_FOLDER_PATH = None

# # 質問セットが保存されるフォルダ
# QUESTIONS_FOLDER_PATH = os.path.join(BASE_DIR, "questions_created_set")
QUESTIONS_FOLDER_PATH = None

# # アップロードした学生たちのリスト
# UPLOADED_STUDENT = {}
UPLOADED_STUDENT = None



DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, "instance", "Lesson04_5.db")}'
UPLOADED_FOLDER_PATH = os.path.join(BASE_DIR, "uploaded")
QUESTIONS_FOLDER_PATH = os.path.join(BASE_DIR, "questions_created_set")

# DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, "1", "instance", "Lesson04_5.db")}'
# UPLOADED_FOLDER_PATH = os.path.join(BASE_DIR, "1", "uploaded")
# QUESTIONS_FOLDER_PATH = os.path.join(BASE_DIR, "1", "questions_created_set")

UPLOADED_STUDENT = {}

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['UPLOAD_FOLDER'] = UPLOADED_FOLDER_PATH

aggregated_comments = []
aggregated_scores = []

data = None

##################### 全角数字を半角にする用 ###################

# 全角数字の範囲と半角数字の範囲を定義
zenkaku_digits = '０１２３４５６７８９'
hankaku_digits = '0123456789'

# 変換テーブルを作成
trans_table = str.maketrans(zenkaku_digits, hankaku_digits)

################################################################



db = SQLAlchemy(app)

### 動作確認済み　
class Post(db.Model): 
    
    student_id_number = db.Column(db.String(15), primary_key = True)
    student_id = db.Column(db.String(15), nullable = False)
    question_number = db.Column(db.String(15), nullable = False)
    score = db.Column(db.Integer(), nullable=True) 
    penalty_comment = db.Column(db.String(300), nullable=True)
    comment = db.Column(db.String(300), nullable=True) 

    def to_dict(self):
        return {
            'score' : self.score,
            'penalty_comment' : self.penalty_comment,
            'comment' : self.comment
        }


# # 今後工事するかも
# @app.route('/start', methods = ['GET','POST'])
# def lesson_number():
    
#     global NOW_LESSON_NUMBER
    
#     if request.method == 'GET':
        
        
@app.route('/', methods = ['GET','POST'])
def lesson_number():
    
    
    
    # global NOW_LESSON_NUMBER
    global NOW_LESSON_NUMBER
    global UPLOADED_FOLDER_PATH
    global DATABASE_URL
    global QUESTIONS_FOLDER_PATH
    global UPLOADED_STUDENT
    global app



    if request.method == 'GET':
        # レッスン番号のリストを作成（ここでは仮のリストを使用）
        # lesson_numbers = [1, 2, 3, 4, 5]
        lesson_numbers = LESSON_NUMBERS
        # HTMLテンプレートをレンダリング
        return render_template('start.html', lesson_numbers=lesson_numbers)

    elif request.method == 'POST':
        # フォームから送信されたレッスン番号を取得
        selected_lesson_number = request.form.get('lesson_number')
        # レッスン番号をグローバル変数に保存
        NOW_LESSON_NUMBER = selected_lesson_number
        
        # # データベースのパス
        # DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, NOW_LESSON_NUMBER, "instance", "Lesson04_5.db")}'

        # # アップロードされたファイルを保存するフォルダを指定
        # UPLOADED_FOLDER_PATH = os.path.join(BASE_DIR, NOW_LESSON_NUMBER, "uploaded")

        # # 質問セットが保存されるフォルダ
        # QUESTIONS_FOLDER_PATH = os.path.join(BASE_DIR, NOW_LESSON_NUMBER, "questions_created_set")

        # # アップロードした学生たちのリスト
        # UPLOADED_STUDENT = {}
        
        
        
        # app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        # app.config['UPLOAD_FOLDER'] = UPLOADED_FOLDER_PATH
        
        
        
        # ホームページにリダイレクト
        # return redirect(url_for('home'))
        return redirect(url_for('student_responses', lesson_number=NOW_LESSON_NUMBER))
    
    


@app.route('/Lesson<int:lesson_number>', methods = ['GET', 'POST'])
def student_responses(lesson_number):

    global data
    global LESSON_NUMBERS
    global NOW_LESSON_NUMBER
    global UPLOADED_STUDENT
    
    files = [f for f in os.listdir(UPLOADED_FOLDER_PATH) if os.path.isfile(os.path.join(UPLOADED_FOLDER_PATH, f)) and f.endswith('.ipynb')]
    UPLOADED_STUDENT = {file_name[:9] : {'student_name' : STUDENT_LIST[file_name[:9]], 'file_name':file_name} for file_name in files}
    # pprint(UPLOADED_STUDENT)
    
    NOW_LESSON_NUMBER = lesson_number

    if request.method == 'GET':  

        if len(os.listdir(UPLOADED_FOLDER_PATH)) > 0:
            pprint(make_csv(UPLOADED_FOLDER_PATH))
            # data = pd.read_csv(rf"{os.getcwd()[0]}:\マイドライブ\flask_tutrial\test.csv")
            data = pd.read_csv(os.path.join(BASE_DIR, "test.csv"))
            data = data.sort_values('student_id')
        
        ################### Menuの設問文 #######################
        dropdown_items = [{"name": f"{number}", "number": f"{value}"} for number, value in QUESTIONS_NUMBER.items()] 
        
        ################### 取得したファイルの表示 ###############
        uploaded_files = [f for f in os.listdir(UPLOADED_FOLDER_PATH) if os.path.isfile(os.path.join(UPLOADED_FOLDER_PATH, f)) and f.endswith('.ipynb')]
        uploaded_students = [file_name[:9] for file_name in uploaded_files]

        # print(uploaded_students)
        # print(uploaded_students)

        ################### テーブル形式でコメント，点数を表示 #############
        posts = Post.query.all()


        # ここで 'DATABASE_URI' は実際のデータベースのURIに置き換える必要があります。
        engine = create_engine(DATABASE_URL)

        # SQLクエリを直接実行
        df = pd.read_sql("SELECT * FROM post", engine)



        data_structure = {}
        for post in posts:
            if post.student_id not in data_structure:
                data_structure[post.student_id] = {}
            data_structure[post.student_id][post.question_number] = post.to_dict()

        # print(data_structure)
        for student_id, value in data_structure.items():
            # print(student_id, value)
            p_comment = '● 減点箇所\n'
            other_comment = '● その他コメント\n'

            for key, v in value.items():
                # print(key, v['penalty_comment'], v['comment'])
                if len(v['penalty_comment']) > 0:
                    p_comment += f'- {QUESTIONS_NAME[key]} : ' + v['penalty_comment'] + '\n'
                if len(v['comment']) > 0:
                    other_comment += f'- {QUESTIONS_NAME[key]} : ' + v['comment'] + '\n'

            if p_comment == '● 減点箇所\n':
                p_comment += '- なし\n'
            full_comment = p_comment + other_comment
            # full_comment = full_comment.replace('\n', '<br>')

            data_structure[student_id]['full_comment'] = full_comment
            if student_id in uploaded_students:
                data_structure[student_id]['file_name'] = UPLOADED_STUDENT[student_id]['file_name']
            else:
                data_structure[student_id]['file_name'] = ''

        
        max_assignments = len(QUESTIONS_NUMBER.values()) + 1   # ここで課題の数を指定する．     
        # print(max_assignments)
        

        if NOW_LESSON_NUMBER is None:
            NOW_LESSON_NUMBER = LESSON_NUMBERS[-1]
        else:
            print(NOW_LESSON_NUMBER)


        # return render_template('student.html', dropdown_items=dropdown_items, students_list = students_list)
        return render_template('student.html', dropdown_items=dropdown_items, dict_data=data_structure, max_assignments=max_assignments, students_list=STUDENT_LIST, uploaded_students=uploaded_students, questions_name=QUESTIONS_NAME, lesson_numbers=LESSON_NUMBERS, now_lesson_number=NOW_LESSON_NUMBER)

    if request.method == 'POST':

        
        new_lesson_number = request.form.get('new_lesson_number')
        
        
        # 新しいレッスン番号を追加
        LESSON_NUMBERS.append(new_lesson_number)

        LESSON_NUMBERS = sorted(set(LESSON_NUMBERS))

        # ファイルにレッスン番号を保存
        with open('lesson_number.py', 'w') as f:
            f.write(f"lesson_numbers = {LESSON_NUMBERS}")
            
        # return redirect('/')
        return redirect(url_for('student_responses', lesson_number=NOW_LESSON_NUMBER))


@app.route('/add_lesson', methods=['POST'])
def add_lesson():
    
    global LESSON_NUMBERS
    
    new_lesson_number = request.form.get('new_lesson_number')
    
    # 新しいレッスン番号を追加
    LESSON_NUMBERS.append(new_lesson_number)

    LESSON_NUMBERS = sorted(set(LESSON_NUMBERS))

    # ファイルにレッスン番号を保存
    with open('lesson_number.py', 'w') as f:
        f.write(f"lesson_numbers = {LESSON_NUMBERS}")

    # return redirect('/')
    return redirect(url_for('student_responses', lesson_number=NOW_LESSON_NUMBER))


# @app.route('/lesson/<int:number>', methods=['POST'])
# def lesson(number):
    
#     global NOW_LESSON_NUMBER
    
#     if request.method == 'POST':
        
#         # number= request.form.get('number')
#         print(number)
#         NOW_LESSON_NUMBER = number
        
#         # return redirect('/')
#         return redirect(url_for('student_responses', lesson_number=NOW_LESSON_NUMBER))







@app.route('/upload', methods=['GET', 'POST'])
def upload():

    global UPLOADED_STUDENT

    if request.method == 'GET':
        
        files = [f for f in os.listdir(UPLOADED_FOLDER_PATH) if os.path.isfile(os.path.join(UPLOADED_FOLDER_PATH, f)) and f.endswith('.ipynb')]
        
        # 実行するごとにhtmlファイルを生成 しかし，時間が掛かるのでアクセスごとにhtmlを作成する．
        # for file in files:
        #     file_path = UPLOADED_FOLDER_PATH + '\\' + file
        #     os.system(f"jupyter nbconvert --to html {file_path}") 

        UPLOADED_STUDENT = {file_name[:9] : {'student_name' : STUDENT_LIST[file_name[:9]], 'file_name':file_name} for file_name in files}
            
        # pprint(files)
        UPLOADED_STUDENT = dict(sorted(UPLOADED_STUDENT.items(), key=lambda x:x[0]))
        # UPLOADED_STUDENT = sorted(UPLOADED_STUDENT)
        # pprint(files)
        # pprint(UPLOADED_STUDENT)
        return render_template('upload.html', files = files, student_list = UPLOADED_STUDENT)
    

    if request.method == 'POST':
        uploaded_files = request.files.getlist('files[]')  # 複数ファイルを取得

        if not uploaded_files:
            return jsonify({'message': 'No files for upload'}), 400

        try:
            for file in uploaded_files:
                if file.filename == '':
                    continue  # ファイル名がないファイルは無視
                if file:
                    filename = secure_filename(file.filename)
                    filename = filename[:9] + '@' + filename[9:]
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # flash('Files successfully uploaded', 'success')  # 成功のフラッシュメッセージ # なぜかうまくいかない


            return redirect('/')  # Homeにリダイレクト
        except Exception as e:

            # flash(f'An error occurred: {e}', 'error')  # エラーのフラッシュメッセージ
            
            return redirect('/upload')


from test_ipynb2html import convert_ipynb_to_html


@app.route('/read_ipynb/<filename>')
@app.route('/read_ipynb/<filename>/<question_number>')
def read_ipynb(filename, question_number=None):
    file_path = os.path.join(UPLOADED_FOLDER_PATH, filename)
    output_file_path = file_path.replace('.ipynb', '.html')
    # print(output_file_path)

    if not os.path.exists(output_file_path):
        # JupyterノートブックをHTMLに変換
        
        convert_ipynb_to_html(file_path)
        
        # print(file_path)
        # file_path = 'H:\\マイドライブ\\flask_tutrial\\uploaded\\2022104780012022104789Lesson05_202210478-20231027_v2.ipynb'
        # subprocess.run(["jupyter", "nbconvert", "--to", "html", file_path], check=True)

    # HTMLファイルの内容を読み込む
    with open(output_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    section_id = None
    if question_number:
        # BeautifulSoupを使ってHTMLを解析
        soup = BeautifulSoup(html_content, 'html.parser')

        # 問題文に該当する部分を検索
        
        question_text = [key for key, value in QUESTIONS_NUMBER.items() if value == str(question_number)][0].replace('## ', '')
        
        
        anchor = None
        section_id = None
        
        section = soup.find(string=question_text)
        if section:
        
            anchor = section.find_previous("a", class_="anchor-link")
            # print(anchor)
            
            
            # 問題文に該当する部分を検索
            
            if anchor and anchor.has_attr('href'):
                section_id = anchor['href'].lstrip('#')
                # HTML内容とセクションIDをページに表示
                # print(anchor['href'])
                # print('section_id : ',section_id)
                return render_template('read_ipynb.html', html_content=html_content, section_id=section_id)

    # HTML内容とセクションIDをページに表示
    return render_template_string(html_content)



@app.route('/delete_all')
def delete_all():
    # UPLOADED_FOLDER_PATH から全てのファイルを削除するコード
    for f in os.listdir(UPLOADED_FOLDER_PATH):
        file_path = os.path.join(UPLOADED_FOLDER_PATH, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
            
    # ファイル削除時にUPLOADED_STUDENTを更新
    global UPLOADED_STUDENT
    files = [f for f in os.listdir(UPLOADED_FOLDER_PATH) if os.path.isfile(os.path.join(UPLOADED_FOLDER_PATH, f)) and f.endswith('.ipynb')]
    UPLOADED_STUDENT = {file_name[:9] : {'student_name' : STUDENT_LIST[file_name[:9]], 'file_name':file_name} for file_name in files}

    # 削除後、アップロードページにリダイレクト
    return redirect(url_for('upload'))



@app.route('/delete_file/<filename>')
def delete_file(filename):
    file_path = os.path.join(UPLOADED_FOLDER_PATH, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        if os.path.exists(file_path.replace('.ipynb', '.html')):
            os.remove(file_path.replace('.ipynb', '.html'))
        # flash(f'{filename} was successfully deleted.')  # オプション: ユーザーに通知する
    else:
        # flash(f'{filename} does not exist.')  # オプション: ファイルが存在しない場合の通知
        pass
    
    # ファイル削除時にUPLOADED_STUDENTを更新
    global UPLOADED_STUDENT
    files = [f for f in os.listdir(UPLOADED_FOLDER_PATH) if os.path.isfile(os.path.join(UPLOADED_FOLDER_PATH, f)) and f.endswith('.ipynb')]
    UPLOADED_STUDENT = {file_name[:9] : {'student_name' : STUDENT_LIST[file_name[:9]], 'file_name':file_name} for file_name in files}
    
    return redirect("/upload")  # ファイルリストのページにリダイレクト






@app.route('/create-questions', methods=['POST', 'GET'])
def create_questions():

    if request.method == 'GET':
            # questions.py の内容を読み込む
            try:
                from questions_created_set.questions import questions, questions_number, questions_name_to_number
            except ImportError as e:
                # ファイルがないか変数が定義されていない場合はエラーメッセージを設定
                questions = {}
                questions_number = {}
                questions_name_to_number = {}
                error_message = str(e)

            # テンプレートに変数の内容を渡す
            return render_template('questions_created.html', existing_questions=questions, existing_numbers=questions_number, existing_names=questions_name_to_number, error=error_message if 'error_message' in locals() else None)
    
    if request.method == 'POST':
        question_texts = request.form.getlist('question_text[]')
        answer_counts = request.form.getlist('answer_count[]')
        question_names = request.form.getlist('question_name[]')

        # 質問番号は自動的に1から始まる連番とする
        question_numbers = list(range(1, len(question_texts) + 1))

        # questions と questions_number の辞書を作成
        questions = {text: int(count) for text, count in zip(question_texts, answer_counts)}
        questions_number = {text: str(num) for text, num in zip(question_texts, question_numbers)}
        
        # 設問名と番号の対応辞書を作成
        questions_name_to_number = {str(num): name for name, num in zip(question_names, question_numbers)}

        # questions_file_path = QUESTIONS_FOLDER_PATH + '\\questions.py'
        questions_file_path = os.path.join(QUESTIONS_FOLDER_PATH, "questions.py")

        
        # 辞書をファイルに書き出す
        # with open(QUESTIONS_FOLDER_PATH + '\\questions.py', 'w', encoding='utf-8') as f:
        with open(os.path.join(QUESTIONS_FOLDER_PATH, "questions.py"), 'w', encoding='utf-8') as f:
            f.write(f'questions = {json.dumps(questions, ensure_ascii=False, indent=4)}\n')
            f.write(f'questions_number = {json.dumps(questions_number, ensure_ascii=False, indent=4)}\n')
            f.write(f'questions_name_to_number = {json.dumps(questions_name_to_number, ensure_ascii=False, indent=4)}\n')




        # 設問を追加した際にDBに追加の主キーを作成してデータベースに挿入

        for question_number in questions_number.values():
            
            if Post.query.filter_by(question_number = question_number).count() == 0:

                for student_id in STUDENT_LIST:

                    # 主キーを作成
                    student_id_number = f"{student_id}_{question_number}"

                    post = Post(student_id_number = student_id_number, 
                                student_id = student_id, 
                                question_number = question_number, 
                                score = '',
                                penalty_comment = '',
                                comment = '')

                    db.session.add(post)

                db.session.commit()


        return redirect('/')
    





# @app.route('/<int:number>', methods = ['GET', 'POST'])
# def question(number):
@app.route('/Lesson<int:lesson_number>/<int:question_number>', methods = ['GET', 'POST'])
def question(lesson_number, question_number):
    
    # 変数の再定義のタイミングを検討する必要がある．のちに変更するかも
    global UPLOADED_STUDENT
    files = [f for f in os.listdir(UPLOADED_FOLDER_PATH) if os.path.isfile(os.path.join(UPLOADED_FOLDER_PATH, f)) and f.endswith('.ipynb')]
    UPLOADED_STUDENT = {file_name[:9] : {'student_name' : STUDENT_LIST[file_name[:9]], 'file_name':file_name} for file_name in files}
    
    
    # print(UPLOADED_STUDENT['202310038']['file_name'])
    
    if request.method == 'GET':

        if data is None or len(QUESTIONS_NUMBER) == 0 or len(UPLOADED_STUDENT) == 0: 
            return redirect ('/')
            
        minimal_data = extract_df(data, question_number) 
        
        ########## numberに対応する問題文の取得 ###########
        question_text = [key for key, value in QUESTIONS_NUMBER.items() if value == str(question_number)][0].replace('## ', '')
            
        ########## メニューの内容 ###########
        dropdown_items = [{"name": f"{num}", "number": f"{value}"} for num, value in QUESTIONS_NUMBER.items() if question_number != int(value)]

        ######### カラムの行の入れ替え（色付け用） ###########
        columns = minimal_data.columns.tolist()
        
        # `_unique` サフィックスのカラムとその前のカラムを逆の順番にする
        new_columns = []
        i = 0
        while i < len(columns):
            if i < len(columns) - 1 and '_unique' in columns[i + 1]:
                new_columns.append(columns[i + 1])
                new_columns.append(columns[i])
                i += 2
            else:
                new_columns.append(columns[i])
                i += 1

        # 新しいカラムの順番で DataFrame を更新
        minimal_data = minimal_data[new_columns]

        ################################
                
        student_ids = minimal_data['student_id'].tolist()

        # student_idがstudent_idsリストに含まれ、かつ特定のquestion_numberに一致するレコードを取得
        student_posts = Post.query.filter(Post.student_id.in_(student_ids), Post.question_number == str(question_number)).all()
        
        
        # # 取得したレコードをループ処理
        # for post in student_posts:
        #     print(post.student_id_number, post.score, post.penalty_comment, post.comment)

        # # Post のデータを student_id をキーにした辞書に変換
        # posts_dict = {post.student_id: post for post in student_posts}
        
        # for id, post in posts_dict.items():
        #     print(id, post.student_id_number, post.score, post.penalty_comment, post.comment)
        
        # Post のデータを student_id_number をキーにした辞書に変換
        posts_dict = {post.student_id_number: post for post in student_posts}

        # 辞書からデータを取り出して minimal_data に列を追加
        # student_id_number を生成してその値を使って辞書を参照する
        minimal_data['score'] = minimal_data.apply(lambda row: getattr(posts_dict.get(f"{row['student_id']}_{question_number}"), 'score', ''), axis=1)
        minimal_data['penalty_comment'] = minimal_data.apply(lambda row: getattr(posts_dict.get(f"{row['student_id']}_{question_number}"), 'penalty_comment', ''), axis=1)
        minimal_data['comment'] = minimal_data.apply(lambda row: getattr(posts_dict.get(f"{row['student_id']}_{question_number}"), 'comment', ''), axis=1)
        
        minimal_data['file_name'] = minimal_data.apply(lambda row: f"{UPLOADED_STUDENT[str(row['student_id'])]['file_name']}", axis=1)
                

        # print(minimal_data[['student_id','score', 'penalty_comment', 'comment']])
        # print(minimal_data)
        
        print(question_text)
        

        return render_template('question.html', dropdown_items=dropdown_items, minimal_data=minimal_data, lesson_number=lesson_number ,number=question_number, question_text=question_text, columns=columns, students_list = STUDENT_LIST, now_lesson_number=lesson_number)

    if request.method == 'POST':
        form_data = request.form
        
        parsed_data = {}

        # フォームデータの処理，データを整形して取得
        for key, value in form_data.items():
            # キーから student_id と number を取得
            match = re.match(r"(\w+)_\((\d+), (\d+)\)", key)
            # print(f'match {match.groups()}, value {value}')
            if match:
                field_name = match.group(1)  # 'score', 'GentenComments', or 'comments'
                student_id_number = match.group(2) + '_' + match.group(3)
                
                # parsed_data にまだその生徒のデータがなければ辞書を作成
                if student_id_number not in parsed_data:
                    parsed_data[student_id_number] = {'score': '', 'penalty_comment': '', 'comment': ''}
                
                # スコアの場合は整数に変換
                if field_name == 'score':
                    # 全角数字を半角数字に変換
                    value = value.translate(trans_table)
                    # 数値に変換可能かチェックし、可能であれば変換
                    parsed_data[student_id_number]['score'] = int(value) if value.isdigit() else ''
                
                # コメントの場合はそのまま格納
                elif field_name == 'GentenComments':
                    parsed_data[student_id_number]['penalty_comment'] = value
                
                elif field_name == 'comments':
                    parsed_data[student_id_number]['comment'] = value

        # print(parsed_data)

        # データベースに保存
        for student_id_number, posted_data in parsed_data.items():

            # 学生IDと設問番号をキーに持つPostインスタンスを検索
            post = Post.query.filter_by(student_id_number = student_id_number).first()
            if post:
                # 存在する場合は更新
                post.score = posted_data['score']
                post.penalty_comment = posted_data['penalty_comment']
                post.comment = posted_data['comment']
            else:
                # 存在しない場合は新規作成
                new_post = Post(
                    student_id_number = student_id_number,
                    score=posted_data['score'],
                    penalty_comment=posted_data['penalty_comment'],
                    comment=posted_data['comment']
                )
                db.session.add(new_post)
        
        try:
            db.session.commit()
            # return "Data received and stored", 200
            return redirect('/') 
        except IntegrityError as e:
            db.session.rollback()
            # エラー処理...
            return "An error occurred while storing the data", 500
        # return "Data received and stored", 200

    return "This endpoint expects a POST request."            





# from students_list import students_list
from sqlalchemy import inspect


def reset_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # 主キーを作成してデータベースに挿入
        for question_number in QUESTIONS_NUMBER.values(): 

            for student_id in STUDENT_LIST:

                # 主キーを作成
                student_id_number = f"{student_id}_{question_number}"

                post = Post(student_id_number = student_id_number, 
                            student_id = student_id, 
                            question_number = question_number, 
                            score = '',
                            penalty_comment = '',
                            comment = '')

                db.session.add(post)

        db.session.commit()



if __name__ == '__main__':
    
    with app.app_context():
        # データベースにstudentsテーブルが存在するかどうかをチェック
        inspector = inspect(db.engine)
        if 'post' not in inspector.get_table_names():
            reset_database()
            
    app.run(debug=True)
