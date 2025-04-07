const profileName = "default";
let selectedTask;

async function send_profile_request() {
    const url = `/api/profile/${profileName}`;

    try {
        const response = await fetch(url, {
            method: "GET"
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const json = await response.json();
        return json;

    } catch (error) {
        console.error(error.message);
        return -1;
    }
}

async function send_setting_catagory_request(catagoryName) {
    const url = `/api/settings/${catagoryName}`;

    try {
        const response = await fetch(url, {
            method: "GET"
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const html = await response.text();
        return html;

    } catch (error) {
        console.error(error.message);
        return -1;
    }
}

async function send_form(form) {
    const formData = new FormData(form);
    const formCatagory = form.getAttribute("data-catagory");
    try {
        const response = await fetch("/api/saveprofile", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "form": formData,
                "catagory": formCatagory,
                "task": selectedTask,
                "profile": profileName
            })
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
    } catch (e) {
        console.error(e);
        alert("Der skete en fejl, indstillingerne blev ikke gemt! Prøv igen.");
    }
}

async function main() {
    // Get profile
    let profile = await send_profile_request();
    if (profile == -1 || profile == {}) {
        alert("Fejl! Profilen kunne ikke indlæses!");
        return;
    }
    // Display selected and unselected elements
    const selectedHTMLElement = document.getElementById("selected");
    const unselectedHTMLList = document.getElementById("unselected-parent");
    let selectedIndex = selectedHTMLElement.getAttribute('data-index');
    for (i = 0; i < profile.tasks.length; i++) {
        if (profile.tasks[i].id.toString() == selectedIndex) {
            selectedTask = profile.tasks[i];
            selectedHTMLElement.innerHTML = profile.task_name_prefix + " " + profile.tasks[i].id.toString() + ": " + selectedTask.settings.general.name.value;
            document.getElementById("selected-taskname-header").innerHTML = selectedHTMLElement.innerHTML;
        } else {
            let li = document.createElement("li");
            let a = document.createElement("a");
            a.href = "/?selected=" + profile.tasks[i].id.toString();
            a.innerHTML = profile.task_name_prefix + " " + profile.tasks[i].id.toString() + ": " + profile.tasks[i].settings.general.name.value;
            li.appendChild(a);
            unselectedHTMLList.appendChild(li);
        }
    }
    if (!selectedTask) {
        alert("Fejl! Den valgte opgave eksisterer ikke i den valgte profil!");
        return;
    }

    // Build settings page
    settingsParent = document.getElementById("settings-parent");
    for (const [key, value] of Object.entries(selectedTask.settings)) {
        let htmlRecieved = await send_setting_catagory_request(key);
        if (htmlRecieved == -1) {
            alert("Fejl! Indstillingskatagorien " + key + " kunne ikke indlæses.")
        } else {
            settingsParent.innerHTML = settingsParent.innerHTML + htmlRecieved;
        }
    }
    // Add event listeners to all settings forms on submit for custom submit event
    const allForms = document.querySelectorAll('.form');
    for (i = 0; i < allForms.length; i ++) {
        allForms[i].addEventListener("submit", (event) => {
            event.preventDefault();
            send_form(event.target);
        });
    }

    // Display loaded values from profile (displays current settings)
    for (const [setting, properties] of Object.entries(selectedTask.settings)) {
        for (const [property, content] of Object.entries(properties)) {
            console.log(content)
            // Loading depends on type
            if (content.type == "text") {
                document.getElementById(content.elementID).value = content.value;
            }
        }
    }
}

// When page is initially loaded, load content from server
document.addEventListener('DOMContentLoaded', async () => {
    await main()
});