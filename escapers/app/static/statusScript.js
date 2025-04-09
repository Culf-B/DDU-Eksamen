async function sendGameUpdateRequest(newState) {
    const url = '/api/update_game_state/' + newState
    try {
        const response = await fetch(url, {method: "GET"});
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
    } catch (error) {
        console.error(error.message);
    }
}
async function beginGame() {
    await sendGameUpdateRequest("started"); 
}
async function pauseGame() {
    await sendGameUpdateRequest("paused"); 
}
async function endGame() {
    await sendGameUpdateRequest("ended"); 
}

async function update_status() {
    const timer_paragraph = document.getElementById("timer_paragraph");
    const task_list = document.getElementById("tasks");
    let json;

    const url = '/api/game_status'
    try {
        const response = await fetch(url, {method: "GET"});
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        json = await response.json();

    } catch (error) {
        console.error(error.message);
        return
    }

    // Format time in timer
    let totalTime = json.totaltime;

    let hours = Math.floor(totalTime / 3600);
    let minutes = Math.floor(totalTime / 60);
    let seconds = Math.floor(totalTime % 60);

    let formattedTime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

    timer_paragraph.innerHTML = formattedTime;

    // Update tasklist
    task_list.innerHTML = ""

    for ([key, value] of Object.entries(json.tasks)) {
        let taskElement = document.createElement("li");
        if (value.open == false && value.solved == false) {
            taskElement.setAttribute("class", "task-locked");
        } else if (value.open == true && value.solved == false) {
            taskElement.setAttribute("class", "task-open")
        } else if (value.solved == true) {
            taskElement.setAttribute("class", "task-complete")
        }
        let taskLinkElement = document.createElement("a");
        taskLinkElement.innerHTML = key;
        taskElement.appendChild(taskLinkElement);
        task_list.appendChild(taskElement);
        
    }


    console.log("Status updated!");
}
setInterval(update_status, 1000);