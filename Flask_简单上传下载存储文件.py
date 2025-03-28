"""
### 中文介绍：
这个Flask应用实现了文件上传、文件列表展示、文件下载、文件删除和文件重命名功能。
用户可以通过浏览器上传文件，所有上传的文件会显示在一个文件列表页面。
每个文件都可以通过右键菜单进行删除或重命名操作。删除和重命名操作需要用户确认，并通过AJAX进行异步处理。
此外，文件下载功能需要用户进行基本认证。
文件名会被安全地处理，以防止潜在的安全问题。这个应用适用于需要简单文件管理的场景。
### English Introduction:
This Flask application provides functionality for file uploading, listing, downloading, deleting, and renaming. 
Users can upload files via the browser, and all uploaded files are displayed on a file list page. 
Each file can be deleted or renamed via a right-click menu. Deletion and renaming operations require user confirmation and are handled asynchronously using AJAX. 
Additionally, file downloads require basic authentication. Filenames are sanitized to prevent potential security issues. 
This application is suitable for scenarios that require simple file management.
"""
from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
app = Flask(__name__)
auth = HTTPBasicAuth()
# 配置
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 创建上传文件夹
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# 用户数据
users = {
    "admin": generate_password_hash("admin-auth")  ################你需要在这里设定你的密码，防止别人下载和删除你的文件。
}
# ------------------ 用户认证 ------------------
@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
# ------------------ 文件名处理 ------------------
def sanitize_filename(filename):
    """
    允许的字符：字母、数字、下划线、点和破折号
    """
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
# ------------------ 文件上传 ------------------
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 判断是否有文件
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # 判断文件名是否为空
        if file.filename == '':
            return redirect(request.url)
        # 对文件名进行安全处理
        filename = sanitize_filename(file.filename)
        # 保存文件
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_files'))
    # 显示上传表单
    return render_template_string(UPLOAD_FORM_TEMPLATE)
# ------------------ 列出文件 ------------------
@app.route('/files')
def uploaded_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string(FILE_LIST_TEMPLATE, files=files)
# ------------------ 下载文件 ------------------
@app.route('/uploads/<filename>')
@auth.login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
# ------------------ 删除文件 ------------------
@app.route('/delete/<filename>', methods=['POST'])
@auth.login_required
def delete_file(filename):
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
# ------------------ 重命名文件 ------------------
@app.route('/rename/<filename>', methods=['POST'])
@auth.login_required
def rename_file(filename):
    new_name = request.form.get('new_name')
    # 检查新文件名是否为空
    if not new_name:
        return jsonify({'status': 'error', 'message': 'New filename is required.'})
    # 对新文件名进行安全处理
    sanitized_new_name = sanitize_filename(new_name)
    # 定义文件路径
    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], sanitized_new_name)
    try:
        # 执行重命名
        os.rename(old_file_path, new_file_path)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
# ------------------ HTML 模板 ------------------
UPLOAD_FORM_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>Upload new File</title>
    <style>
        body { background-color: #e8f5e9; }
        .container { margin-top: 50px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-success">Upload new File</h1>
        <form method="post" enctype="multipart/form-data">
            <div class="form-group">
                <input type="file" name="file" class="form-control-file">
            </div>
            <button type="submit" class="btn btn-success">Upload</button>
        </form>
    </div>
</body>
</html>
'''
FILE_LIST_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <title>Uploaded Files</title>
    <style>
        body { background-color: #e8f5e9; }
        .container { margin-top: 50px; }
        .file-list { list-style-type: none; padding: 0; }
        .file-list li { padding: 10px; background-color: #f1f8e9; margin-bottom: 5px; border-radius: 5px; }
        .file-list li:hover { background-color: #c8e6c9; cursor: pointer; }
        /* Right-click menu */
        .context-menu {
            display: none;
            position: absolute;
            background-color: white;
            border: 1px solid #ccc;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            border-radius: 5px;
        }
        .context-menu a {
            display: block;
            padding: 10px;
            text-decoration: none;
            color: black;
        }
        .context-menu a:hover {
            background-color: #e8e8e8;
        }
    </style>
    <script>
        $(document).ready(function() {
            // 创建右键菜单
            var $contextMenu = $('<div class="context-menu"><a href="#" id="rename">Rename</a><a href="#" id="delete">Delete</a></div>');
            $('body').append($contextMenu);

            // 右键点击文件时，显示菜单
            $('.file-list li').on('contextmenu', function(e) {
                e.preventDefault();
                var filename = $(this).data('filename');
                $contextMenu.css({
                    top: e.pageY + 'px',
                    left: e.pageX + 'px'
                }).show();
                
                // 将文件名赋值给菜单项
                $('#rename').data('filename', filename);
                $('#delete').data('filename', filename);
            });

            // 点击页面其他地方隐藏菜单
            $(document).click(function() {
                $contextMenu.hide();
            });

            // 点击重命名时，调用AJAX请求进行重命名
            $('#rename').click(function() {
                var filename = $(this).data('filename');
                var newName = prompt("Enter new filename:", filename);
                if (newName && newName !== filename) {
                    $.ajax({
                        url: '/rename/' + filename,
                        type: 'POST',
                        data: { new_name: newName },
                        success: function(response) {
                            if (response.status === 'success') {
                                location.reload();
                            } else {
                                alert('Error: ' + response.message);
                            }
                        }
                    });
                }
                $contextMenu.hide();
            });

            // 点击删除时，调用AJAX请求进行删除
            $('#delete').click(function() {
                var filename = $(this).data('filename');
                if (confirm('Are you sure you want to delete ' + filename + '?')) {
                    $.ajax({
                        url: '/delete/' + filename,
                        type: 'POST',
                        success: function(response) {
                            if (response.status === 'success') {
                                location.reload();
                            } else {
                                alert('Error: ' + response.message);
                            }
                        }
                    });
                }
                $contextMenu.hide();
            });
        });
    </script>
</head>
<body>
    <div class="container">
        <h1 class="text-success">Uploaded Files</h1>
        <ul class="file-list">
        {% for file in files %}
            <li data-filename="{{ file }}">
                <a href="{{ url_for('download_file', filename=file) }}" class="text-success">{{ file }}</a>
            </li>
        {% endfor %}
        </ul>
    </div>
</body>
</html>
'''
if __name__ == '__main__':
    app.run(debug=False)
