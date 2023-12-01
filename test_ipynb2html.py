from nbconvert import HTMLExporter
import nbformat

def convert_ipynb_to_html(file_path):
    
    output_file_path = file_path.replace('.ipynb', '.html')
    
    # ノートブックを読み込む
    with open(file_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    # HTMLエクスポーターを作成
    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic'  # もしくは 'lab' を使用

    # HTMLに変換
    (body, resources) = html_exporter.from_notebook_node(notebook)

    # HTMLファイルとして出力
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(body)

# この関数を使って変換を実行
# convert_ipynb_to_html('path_to_your_ipynb_file.ipynb', 'output_html_file.html')

if __name__ == '__main__':
    convert_ipynb_to_html('test.ipynb')