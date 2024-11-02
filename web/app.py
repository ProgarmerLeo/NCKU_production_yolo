from flask import Flask, jsonify, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_stats')
def get_stats():
    with open(r'C:\Users\HanX\Desktop\NCKU__proj\web\data.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/emergency_stop', methods=['POST'])
def emergency_stop():
    with open(r'C:\Users\HanX\Desktop\NCKU__proj\web\data.json', 'r+') as f:
        data = json.load(f)
        data['em_stop'] = True
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    return jsonify({"status": "Emergency stop activated"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
