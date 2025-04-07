from flask import Flask, url_for, render_template, request
import os
import json

class ProfileManager:
    def __init__(self, path):
        self.path = path
        self.validProfilesList = []
    
    def updateValidProfilesList(self):
        for f in os.listdir(self.path):
            if f.endswith(".json"):
                self.validProfilesList.append(f)

    def getProfile(self, name):
        filename = name + ".json"
        if filename in self.validProfilesList:
            with open(os.path.join(self.path, filename), "r") as f:
                jsonData = json.load(f)
            return jsonData
        else:
            print(f'File {filename} is not a valid profile!')
            return {}
        
    def saveProfile(self, profileName, jsonData):
        filename = profileName + ".json"
        with open(os.path.join(self.path, filename), "r") as f:
            json.dump(jsonData, f, indent = 4)


file_path = os.path.abspath(os.path.dirname(__file__))
profileManager = ProfileManager(os.path.join(file_path, "profiles"))
profileManager.updateValidProfilesList()
app = Flask(__name__)

@app.route('/', methods = ['GET'])
def index():
    selected = request.args.get("selected")
    if selected == None:
        selected = 1
    
    css_url = url_for('static', filename = 'style.css')
    script_url = url_for('static', filename = 'script.js')
    return render_template('index.html', css_url = css_url, script_url = script_url, selected_index = selected)

@app.route('/api/profile/<profile>', methods = ['GET'])
def get_profile(profile):
    return profileManager.getProfile(profile)

@app.route('/api/settings/<catagory>', methods = ['GET'])
def get_settings_catagory(catagory):
    pathToHtml = os.path.join(file_path, f'static/forms/{catagory}.html')
    with open(pathToHtml, 'r') as f:
        content = f.read()
    return content

@app.route('/api/saveprofile', methods = ['POST'])
def save_profile():
    try:
        print(request.get_json())
        return {'message': 'Indstillinger gemt!'}, 200
    except Exception as e:
        print(f'Encountered an error: {e}')
        return {'message': 'Fejl! Indstillinger ikke gemt!'}, 500
if __name__ == '__main__':
    app.run(debug = True)