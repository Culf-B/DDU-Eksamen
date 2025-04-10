const profileName = "default";
let selectedTask;
let profile;

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
    let formData = new FormData(form);
    const keys = formData.getAll('keys[]');
    const values = formData.getAll('values[]');
    let data = {};

    if (keys.length > 0) {
        keys.forEach((key, index) => {
            data[key] = values[index]; // You can handle duplicates here if needed
        });
    } else {
        data = Object.fromEntries(formData);
    }

    const formCatagory = form.getAttribute("data-catagory");
    try {
        const response = await fetch("/api/saveprofile", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "form": data,
                "catagory": formCatagory,
                "task": selectedTask.id,
                "profile": profileName
            })
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);

        } else {
            if (formCatagory == "general") {
                set_name_selected(profile.task_name_prefix + " " + selectedTask.id.toString() + ": " + Object.fromEntries(formData).name);
            }
            // Show content saved popup
            const popup = document.getElementById('popup');
            popup.classList.add('show');

            setTimeout(function() {
                popup.classList.remove('show');
            }, 1000);
        }
    } catch (e) {
        console.error(e);
        alert("Der skete en fejl, indstillingerne blev ikke gemt! Prøv igen. Fejlmeddelelse: " + e);
    }
}

function set_name_selected(nameWithPrefix) {
    document.getElementById("selected").innerHTML = nameWithPrefix;
    document.getElementById("selected-taskname-header").innerHTML = nameWithPrefix;
}

async function main() {
    // Get profile
    profile = await send_profile_request();
    if (profile == -1 || profile == {}) {
        alert("Fejl! Profilen kunne ikke indlæses!");
        return;
    }
    // Display selected and unselected elements
    
    const unselectedHTMLList = document.getElementById("unselected-parent");
    let selectedIndex = document.getElementById("selected").getAttribute('data-index');
    for (i = 0; i < profile.tasks.length; i++) {
        if (profile.tasks[i].id.toString() == selectedIndex) {
            selectedTask = profile.tasks[i];
            set_name_selected(profile.task_name_prefix + " " + profile.tasks[i].id.toString() + ": " + selectedTask.settings.general.name.value);
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
    // Execute attached scripts (yes I know this would probably be bad security wise but we are only running this locally)
    const scripts = settingsParent.querySelectorAll('script');
    scripts.forEach(script => {
        const newScript = document.createElement('script');
        if (script.src) {
            newScript.src = script.src;
        } else {
            newScript.textContent = script.textContent;
        }
        document.body.appendChild(newScript); // append to run
    });

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
            // Loading depends on type
            if (content.type == "text") {
                document.getElementById(content.elementID).value = content.value;
            } else if (content.type == "dict") {
                for (const [key, value] of Object.entries(content.value)) {
                    let keyValuePairElement = addKeyValuePair(content.elementID);
                    keyValuePairElement[0].value = key;
                    keyValuePairElement[1].value = value;
                }
            }
        }
    }
}

// When page is initially loaded, load content from server
document.addEventListener('DOMContentLoaded', async () => {
    await main()
});