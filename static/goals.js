const UNITS = {
    'distance': 'mi',
    'elevation': 'ft',
    'duration': 'min'
}

async function fetchGoals() {
    return (await fetch("/goals")).json();
}

function convertUnits(value, category) {
    if (category === 'distance') {
        return Math.round(value / 1609 * 10) / 10;
    }
    else if (category === 'elevation') {
        return Math.round(value * 3.28084 * 10) / 10;
    }
    else if (category === 'duration') {
        return Math.round(value / 60 * 10) / 10;
    }
    else {
        console.log('error in conversion');
        return null;
    }
}

function determineMax(objective, category, timeSpan) {
    if (timeSpan === 'daily-min.') {
        return 7;
    }
    else if (timeSpan === 'daily-avg.' || timeSpan === 'week') {
        return convertUnits(objective, category);
    }
    else {
        console.log("broken!");
        return null;
    }
}

function determineValue(progress, category, time_span) {
    if (time_span === 'daily-min.') {
        return progress;
    }
    else if (time_span === 'daily-avg.') {
        return convertUnits(progress / 7, category);
    }
    else if (time_span === 'week') {
        return convertUnits(progress, category);
    }
    else {
        console.log("couldn't determine value");
        return null;
    }
}

async function updateTable() {
    // get the list of goals from the server
    const goals = await fetchGoals();

    // get a list of all meters so that their values can be used
    const meters = document.querySelectorAll("meter");
    const labels = document.querySelectorAll(".meter-label");

    const table = document.querySelector("table");

    let goalsCompleted = 0;
    meters.forEach((meter, index) => {
        // get the equivalent goal and label for the meter
        const goal = goals[index];
        const label = labels[index];

        // the category and time span values are reused so they're being stored
        const category = goal.category;
        const timeSpan = goal.time_span;

        // calculate max and value of meter based on the goals category and time span
        const max = determineMax(goal.objective, category, timeSpan);
        const value = determineValue(goal.progress, category, timeSpan);

        // update meter with new value
        meter.setAttribute('max', max);
        meter.setAttribute('value', value);
        meter.innerText = value;

        // update label with new value
        label.innerText = `${value}/${max} ` + UNITS[category];
        if (value >= max) {
            label.innerText += "\u2714";
        }
    });
}

updateTable();


const unitLabel = document.getElementById("unit-label");
const categorySelector = document.getElementById("category");
const units = ['mi', 'min', 'ft']
function updateUnitLabel(e) {
    unitLabel.innerText = units[categorySelector.selectedIndex];
    console.log(categorySelector.selectedIndex);
}

categorySelector.addEventListener("change", updateUnitLabel);
updateUnitLabel();