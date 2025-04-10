from flask import Flask, url_for, render_template, request
import os
import json
import time

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
        with open(os.path.join(self.path, filename), "w") as f:
            json.dump(jsonData, f, indent = 4)

class Game:
    def __init__(self, profile, taskIDtoClass):
        self.started = False
        self.paused = False
        self.ended = False
        self.last_time_update = 0
        self.totaltime = 0
        self.finaltime = 0

        self.profile = profile
        self.taskIDtoClass = taskIDtoClass
        self.tasks = {}

        for task in profile["tasks"]:
            if str(task["id"]) in self.taskIDtoClass:
                self.tasks[str(task["id"])] = self.taskIDtoClass[str(task["id"])](task)

    def start(self):
        self.started = True
        self.last_time_update = time.time()

        self.tasks["1"].openTask()
    
    def pause(self):
        self.paused = True
        self.update_total_timer()

    def unpause(self):
        self.paused = False
        self.last_time_update = time.time()        

    def update_total_timer(self):
        self.totaltime += time.time() - self.last_time_update
        self.last_time_update = time.time()

    def end(self):
        self.ended = True
        self.update_total_timer()
        self.finaltime = self.totaltime

    def updateTask(self, taskID, deviceInputData):
        if self.started == True and self.paused == False and self.ended == False:
            if taskID in self.tasks:
                self.tasks[taskID].updateValue(deviceInputData)
    
    def get_status_object(self):
        if self.started and not self.ended and not self.paused:
            self.update_total_timer()
        self.status_object = {
            "started": self.started,
            "paused": self.paused,
            "ended": self.ended,
            "totaltime": self.totaltime,
            "finaltime": self.finaltime,
            "tasks": {}
        }
        for ID, task in self.tasks.items():
            self.status_object["tasks"][f'{self.profile["task_name_prefix"]} {ID}: {task.name}'] = task.getStatus()
        
        return self.status_object


class Task:
    def __init__(self, taskProfileData, ID, isOpen = False):
        self.taskProfileData = taskProfileData
        self.ID = ID
        self.open = isOpen
        self.solved = False
        self.name = self.taskProfileData["settings"]["general"]["name"]["value"]

    def openTask(self):
        self.open = True

    def getStatus(self):
        return {"open": self.open, "solved": self.solved}

class InputMaskine(Task):
    def __init__(self, taskProfileData):
        super().__init__(taskProfileData = taskProfileData, ID = 1)
        self.correct_answer = taskProfileData["settings"]["inputmaskine"]["correct_input"]["value"]
        self.dataDict = {}
        self.solved = False

    def updateValue(self, deviceInputData):
        if self.open:
            self.tempKey, self.tempValue = self.parseRecievedData(deviceInputData)
            self.dataDict[self.tempKey] = self.tempValue
            self.validateAnswer()

    def parseRecievedData(self, recievedData):
        parsedData = recievedData.split(",")
        return parsedData[0], parsedData[1]
    
    def validateAnswer(self):
        for key, value in self.correct_answer.items():
            if not key in self.dataDict:
                return # An answer is missing
            else:
                if not float(self.dataDict[key]) == float(value):
                    return # An answer has the wrong value
                
        # Everything is as it should be, the puzzle is solved
        self.solved = True
        print("solved")

taskIDtoClass = {
    "1": InputMaskine
}

file_path = os.path.abspath(os.path.dirname(__file__))

profileManager = ProfileManager(os.path.join(file_path, "profiles"))
profileManager.updateValidProfilesList()

game = Game(profileManager.getProfile("default"), taskIDtoClass)

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def index():
    selected = request.args.get("selected")
    if selected == None:
        selected = 1
    
    css_url = url_for('static', filename = 'style.css')
    script_url = url_for('static', filename = 'script.js')
    overview_image_url = url_for('static', filename = 'overview.png')
    return render_template(
        'index.html',
        css_url = css_url,
        script_url = script_url,
        selected_index = selected,
        overview_image_url = overview_image_url    
    )

@app.route('/status', methods = ['GET'])
def status():
    css_url = url_for('static', filename = 'style_status.css')
    script_url = url_for('static', filename = 'statusScript.js')
    breakpng_url = url_for('static', filename = 'break.png')
    pausepng_url = url_for('static', filename = 'pause.png')
    startpng_url = url_for('static', filename = 'start.png')
    return render_template(
        'status.html',
        css_url = css_url,
        status_script = script_url,
        breakpng_url = breakpng_url,
        startpng_url = startpng_url,
        pausepng_url = pausepng_url
    )

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
        formDataRecieved = request.get_json()
        print(formDataRecieved)

        # Get profile in its current form
        currentProfile = profileManager.getProfile(formDataRecieved["profile"])
        # Find index for task with given id
        index = None
        for i in range(len(currentProfile["tasks"])):
            if str(currentProfile["tasks"][i]["id"]) == str(formDataRecieved["task"]):
                index = i
        if index == None:
            raise Exception(f'Task with id {formDataRecieved["task"]} does not exist!', 404)

        # Update catagory
        # This code is a crime agains the python interpreter D:
        isDict = False
        catagorySettings = currentProfile["tasks"][index]["settings"][formDataRecieved["catagory"]]
        for key, value in formDataRecieved["form"].items():
            if key in catagorySettings:
                if catagorySettings[key]["type"] == "text":   
                    catagorySettings[key]["value"] = value
            else:
                for setting, setting_value in catagorySettings.items():
                    if setting_value["type"] == "dict":
                        isDict = True
                        catagorySettings[setting]["value"] = formDataRecieved["form"]
                        break
            if isDict:
                break      

        # Add updated catagory to currentProfile
        currentProfile["tasks"][index]["settings"][formDataRecieved["catagory"]] = catagorySettings

        # Save currentProfile to profileManager
        profileManager.saveProfile(formDataRecieved["profile"], currentProfile)

        return {'message': 'Indstillinger gemt!'}, 200
    
    except Exception as e:
        print(f'Encountered an error: {e.args[0]}')
        if len(e.args) > 1:
            return {'message': f'Fejl! {e.args[0]}'}, e.args[1]
        else:
            return {'message': 'Fejl! Indstillinger ikke gemt!'}, 500
    
@app.route('/api/update_device/<device_id>')
def handleDeviceUpdate(device_id):
    try:
        game.updateTask(device_id, request.args.get("data"))
        return "OK", 200
    except Exception as e:
        print(f'An error occured when handling device update: {e}')
        return "Error", 500

@app.route('/api/game_status')
def game_status():
    try:
        return game.get_status_object(), 200
    except Exception as e:
        print("An error occured!", e)
        return "An error occured!", 500

@app.route('/api/update_game_state/<new_state>')
def update_game_state(new_state):
    if (new_state == "started"):
        if game.started == False:
            game.start()
        elif game.paused == True and game.ended == False:
            game.unpause()
        else:
            return "Invalid gamestate", 400
    elif (new_state == "paused"):
        if game.started == True and game.paused == False and game.ended == False:
            game.pause()
        else:
            return "Invalid gamestate", 400
    elif (new_state == "ended"):
        if game.started == True and game.ended == False:
            game.end()
        else:
            return "Invalid gamestate", 400
    else:
        return "Gamestate not found", 404
    return "OK", 200
    

@app.errorhandler(404)
def page_not_found(e):
    return error_page("404: Siden blev ikke fundet"), 404

@app.errorhandler(500)
def page_not_found(e):
    return error_page("500: Der skete en fejl på serveren"), 500

def error_page(message):
    css_url = url_for('static', filename = 'style_errorpage.css')
    error_image_url = url_for('static', filename = 'error.png')
    return render_template('error.html', css_url = css_url, error_image_url = error_image_url, error_message = message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)