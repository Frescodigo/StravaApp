const tableHead = document.getElementById('table-head')
const tableBody = document.getElementById('table-body')

const DAILY_MILES = new Array(371).fill(0.0);

async function getActivities(cutoff) {
  const cutoffInEpoch = Math.floor(cutoff.getTime() / 1000)
  const url = `${APP_URL}/activities?cutoff=${cutoffInEpoch}`
  const response = await fetch(url)
  const activities = await response.json()

  return activities
}

function fillTable() {
  tableBody.innerHTML = '';
  for (let i = 0; i < 7; i++) {
    const dataRow = document.createElement('tr');
    for (let j = 0; j < 53; j++) {
      const tableCell = document.createElement('td');
      tableCell.classList.add('level-1');
      const hiddenData = document.createElement('span');
      hiddenData.classList.add('sr-only');
      hiddenData.innerHTML = DAILY_MILES[7*j + i];
      tableCell.appendChild(hiddenData);
      dataRow.appendChild(tableCell);
    }
    tableBody.appendChild(dataRow);
  }
}

// shit is begging to be refactored
async function updatePage() {
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
  const activities = await getActivities(sundayAYearAgo);

  let mostMilesRanInADay = 0;
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
