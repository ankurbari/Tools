from flask import Flask, request, render_template_string, flash, redirect, url_for
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt'}
app.secret_key = 'supersecretkey'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    vulnerability_information_list = []
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], 'file.txt')
            file.save(filename)

            # Check if the file is empty
            if os.stat(filename).st_size == 0:
                flash('Uploaded file is empty.')
                return redirect(request.url)

            try:
                # Read the data from the uploaded file
                with open(filename, 'r') as f:
                    file_content = f.read()

                # Extract all occurrences of vulnerability_information from the plain text
                start_pos = 0
                while True:
                    start_index = file_content.find('"vulnerability_information"', start_pos)
                    if start_index == -1:
                        break
                    start_index = file_content.find(':', start_index) + 1
                    end_index = file_content.find(',', start_index)
                    if end_index == -1:  # If it's the last field in the file
                        end_index = file_content.find('}', start_index)
                    vulnerability_information = file_content[start_index:end_index].strip().strip('"')
                    vulnerability_information_list.append(vulnerability_information)
                    start_pos = end_index

                if not vulnerability_information_list:
                    flash('No "vulnerability_information" found in the file.')

            except Exception as e:
                flash(f'An error occurred while processing the file: {e}')
                return redirect(request.url)

        else:
            flash('Invalid file type. Only .txt files are allowed.')
            return redirect(request.url)

    # HTML template with form and injected data
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vulnerability Information</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 20px;
            }
            pre {
                white-space: pre-wrap;
                background-color: #f4f4f4;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            form {
                margin-bottom: 20px;
            }
            .flash {
                color: red;
            }
        </style>
    </head>
    <body>
        <h1>Upload Text File</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".txt" required>
            <input type="submit" value="Upload">
        </form>
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        <ul class="flash">
            {% for message in messages %}
            <li>{{ message }}</li>
            {% endfor %}
        </ul>
        {% endif %}
        {% endwith %}
        {% if vulnerability_information_list %}
            <h2>Vulnerability Information</h2>
            {% for info in vulnerability_information_list %}
                <pre>{{ info }}</pre>
            {% endfor %}
        {% endif %}
    </body>
    </html>
    '''
    return render_template_string(html_template, vulnerability_information_list=vulnerability_information_list)

if __name__ == '__main__':
    app.run(debug=True)
