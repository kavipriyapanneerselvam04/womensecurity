async function refreshAlerts() {
    await window.wsApp.loadAlertsTable("alertsTableBody");
}

async function refreshAlertHistory() {
    await window.wsApp.loadAlertsTable("alertHistoryTableBody");
}
