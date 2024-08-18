from flask import Flask, request, render_template_string, jsonify
import requests
import html
from bs4 import BeautifulSoup
from flask_socketio import SocketIO
import threading
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store raw responses and requests in dictionaries
responses = {}
requests_data = {}

html_form = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL and Cookie Input Form</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(to right, #ffecd2, #fcb69f);
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 30px;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        h2 {
            margin-bottom: 20px;
            font-size: 2em;
            color: #333;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            color: #555;
            text-align: left;
        }
        input[type="text"], textarea, select {
            width: 100%;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            border: 2px solid #ddd;
            box-sizing: border-box;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, textarea:focus, select:focus {
            border-color: #fcb69f;
            outline: none;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(to right, #ff6a00, #ee0979);
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1.2em;
            transition: background 0.3s;
        }
        button:hover {
            background: linear-gradient(to right, #ee0979, #ff6a00);
        }
        .results {
            margin-top: 30px;
            text-align: left;
        }
        .results h3 {
            font-size: 1.5em;
            color: #333;
        }
        .results ul {
            list-style-type: none;
            padding: 0;
        }
        .results li {
            margin-bottom: 10px;
        }
        .button {
            display: inline-block;
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            text-decoration: none;
            transition: background-color 0.3s;
            text-align: left;
            width: 100%;
            box-sizing: border-box;
        }
        .button:hover {
            background-color: #0056b3;
        }
        .button-content {
            display: flex;
            justify-content: space-between;
        }
        .response-detail, .request-detail {
            display: none;
            white-space: pre-wrap;
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            margin-top: 10px;
            border-radius: 5px;
            border: 1px solid #555;
            font-family: "Courier New", Courier, monospace;
            overflow: auto;
            max-height: 300px;
        }
        .status-line {
            color: #569cd6;
        }
        .header-key {
            color: #9cdcfe;
        }
        .header-value {
            color: #ce9178;
        }
        .body-content {
            color: #f8f8f2;
            white-space: pre-wrap;
        }
        .html-tag {
            color: #569cd6;
        }
        .html-attribute {
            color: #9cdcfe;
        }
        .html-value {
            color: #ce9178;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>URL and Cookie Input Form</h2>
        <form id="request-form">
            <label for="method">HTTP Method:</label>
            <select id="method" name="method" onchange="toggleBodyField()">
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
            </select>

            <label for="urls">URLs:</label>
            <textarea id="urls" name="urls" rows="4" placeholder="Enter URLs, one per line">{{ urls }}</textarea>

            <label for="cookies">Cookies:</label>
            <textarea id="cookies" name="cookies" rows="4" placeholder="Enter cookies">{{ cookies }}</textarea>

            <label for="headers">Custom Headers (key=value per line):</label>
            <textarea id="headers" name="headers" rows="4" placeholder="Enter custom headers">{{ headers }}</textarea>
            
            <label id="body-label" for="body" style="display: none;">Request Body:</label>
            <textarea id="body" name="body" rows="4" placeholder="Enter request body (for POST and PUT requests)" style="display: none;">{{ body }}</textarea>

            <button type="submit">Submit</button>
        </form>

        <div class="results">
            <h3>Results:</h3>
            <ul id="results-list">
                <!-- Results will be dynamically added here -->
            </ul>
        </div>
    </div>

    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script>
        var socket = io();

        socket.on('update_response', function(data) {
            var listItem = document.createElement('li');
            listItem.innerHTML = `<a href="#" class="button" onclick="showRequestResponse('${data.url.replace(/[^a-zA-Z0-9]/g, '-') }'); return false;">
                                    <div class="button-content">
                                        <span>${data.url}</span>
                                        <span>Status: ${data.status_code}</span>
                                    </div>
                                  </a>
                                  <div id="request-${data.url.replace(/[^a-zA-Z0-9]/g, '-')}" class="request-detail">${data.request}</div>
                                  <div id="response-${data.url.replace(/[^a-zA-Z0-9]/g, '-')}" class="response-detail">${data.response}</div>`;
            document.getElementById('results-list').appendChild(listItem);
        });

        function showRequestResponse(url) {
            var requestElement = document.getElementById('request-' + url);
            var responseElement = document.getElementById('response-' + url);

            if (requestElement.style.display === 'block') {
                requestElement.style.display = 'none';
                responseElement.style.display = 'none';
            } else {
                requestElement.style.display = 'block';
                responseElement.style.display = 'block';
            }
        }

        function toggleBodyField() {
            var method = document.getElementById('method').value;
            var bodyField = document.getElementById('body');
            var bodyLabel = document.getElementById('body-label');

            if (method === 'POST' || method === 'PUT') {
                bodyField.style.display = 'block';
                bodyLabel.style.display = 'block';
            } else {
                bodyField.style.display = 'none';
                bodyLabel.style.display = 'none';
            }
        }

        document.getElementById('request-form').addEventListener('submit', function(e) {
            e.preventDefault();
            var formData = new FormData(this);
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/submit', true);
            xhr.onload = function () {
                if (xhr.status === 200) {
                    console.log('Request submitted.');
                }
            };
            xhr.send(formData);
        });

        document.addEventListener('DOMContentLoaded', function() {
            toggleBodyField();
        });
    </script>
</body>
</html>
'''

def format_headers(headers):
    formatted_headers = ""
    for key, value in headers.items():
        formatted_headers += f"<span class='header-key'>{key}:</span> <span class='header-value'>{value}</span><br>"
    return formatted_headers

def get_raw_response(url, method, headers, cookies, body=None):
    try:
        # Prepare headers and cookies
        headers_dict = {k.strip(): v.strip() for k, v in (header.split('=', 1) for header in headers.splitlines() if '=' in header)}
        cookies_dict = {k.strip(): v.strip() for k, v in (cookie.split('=', 1) for cookie in cookies.splitlines() if '=' in cookie)}
        request_headers = {**headers_dict, **cookies_dict}

        # Make the HTTP request
        if method == 'GET':
            response = requests.get(url, headers=request_headers, verify=False)
        elif method == 'POST':
            response = requests.post(url, headers=request_headers, data=body, verify=False)
        elif method == 'PUT':
            response = requests.put(url, headers=request_headers, data=body, verify=False)
        elif method == 'DELETE':
            response = requests.delete(url, headers=request_headers, verify=False)
        else:
            return "Unsupported HTTP method."

        # Format request and response
        request_info = f"Method: {method}<br>URL: {url}<br>Headers:<br>{format_headers(request_headers)}<br>Body:<br>{html.escape(body or '')}"
        response_info = f"Status: {response.status_code}<br>Headers:<br>{format_headers(response.headers)}<br>Content:<br>{html.escape(response.text)}"

        requests_data[url] = request_info
        responses[url] = response_info

        return {'request': request_info, 'response': response_info, 'status_code': response.status_code}

    except requests.RequestException as e:
        return {'request': f"Error occurred: {str(e)}", 'response': '', 'status_code': 500}

@app.route('/')
def index():
    return render_template_string(html_form)

@app.route('/submit', methods=['POST'])
def submit():
    urls = request.form.get('urls', '').splitlines()
    method = request.form.get('method', 'GET')
    cookies = request.form.get('cookies', '')
    headers = request.form.get('headers', '')
    body = request.form.get('body', '')

    for url in urls:
        url = url.strip()
        if url:
            result = get_raw_response(url, method, headers, cookies, body)
            socketio.emit('update_response', {
                'url': url,
                'request': result['request'],
                'response': result['response'],
                'status_code': result['status_code']
            })
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)