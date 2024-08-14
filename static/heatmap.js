const tableHead = document.getElementById('table-head')
const tableBody = document.getElementById('table-body')

const DAILY_MILES = new Array(371).fill(0.0);

const today = new Date();
const aYearAgo = new Date(
  today.getFullYear() - 1,
  today.getMonth(),
  today.getDate()
);
const sundayAYearAgo = new Date(
  aYearAgo.getFullYear(),
  aYearAgo.getMonth(),
  aYearAgo.getDate() - aYearAgo.getDay()
);

// this is gonna be used to determine which
// color a cell gets in the heatmap
let mostMilesRanInADay = -Infinity;

async function getActivities(cutoff) {
  const cutoffInEpoch = Math.floor(cutoff.getTime() / 1000)
  const url = `${APP_URL}/activities?cutoff=${cutoffInEpoch}`
  const response = await fetch(url)
  const activities = await response.json()

  return activities
}

function fillTable() {
  tableBody.innerHTML = '';

  // this is used to calculate which color the cell
  // should be in the heatmap
  const fifthOfMax = mostMilesRanInADay / 5;

  for (let day = 0; day < 7; day++) {
    const dataRow = document.createElement('tr');

    // should show what day of the week it is =.=
    const weekdayNames = ['', 'Mon', '', 'Wed', '', 'Fri', ''];
    const dayLabelBox = document.createElement('td');
    dayLabelBox.classList.add('day-label-box');
    const dayLabel = document.createElement('span');
    dayLabel.innerHTML = weekdayNames[day];
    dayLabel.classList.add('day-label');
    dayLabelBox.appendChild(dayLabel);
    dataRow.appendChild(dayLabelBox);

    for (let week = 0; week <= 52; week++) {

      const miles = DAILY_MILES[7*week + day];

      let heatmapLevel = Math.floor(miles / mostMilesRanInADay * 5);
      if (heatmapLevel === 5) heatmapLevel = 4;

      const tableCell = document.createElement('td');
      tableCell.classList.add(`level-${heatmapLevel}`);

      const hiddenData = document.createElement('span');
      hiddenData.classList.add('sr-only');

      hiddenData.innerHTML = miles;

      tableCell.appendChild(hiddenData);
      dataRow.appendChild(tableCell);
    }
    tableBody.appendChild(dataRow);
  }
}

// shit is begging to be refactored
async function updatePage() {
  const activities = await getActivities(sundayAYearAgo);

  activities.forEach((activity) => {
    const activityDate = new Date(activity['start_date_local']);
    const timeDeltaInMS = activityDate - sundayAYearAgo;
    const msInADay = 86400000;
    const timeDeltaInDays = Math.floor(timeDeltaInMS / msInADay);
    const distanceInMi = activity['distance'] / 1609;
    DAILY_MILES[timeDeltaInDays] += distanceInMi;
    if (DAILY_MILES[timeDeltaInDays] > mostMilesRanInADay) mostMilesRanInADay = DAILY_MILES[timeDeltaInDays];
  });

  console.log(DAILY_MILES);

  fillTable();

  const waitingBox = document.getElementById('waiting-box');
  waitingBox.innerHTML = '';
}


fillTable()
updatePage()
