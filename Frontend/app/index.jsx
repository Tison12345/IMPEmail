// import React from 'react'
// import { Redirect } from 'expo-router';
// import { StyleSheet } from 'react-native';

// export default function Index() {
//   return <Redirect href="/(auth)/SignIn" />;
// }

// const styles = StyleSheet.create({
//   container: {
//     flex: 1,
//   },
// });
// import React, { useEffect } from 'react';
// import { Redirect } from 'expo-router';
// import { StyleSheet } from 'react-native';
// import * as Notifications from 'expo-notifications';

// // Set up the notification handler
// Notifications.setNotificationHandler({
//   handleNotification: async () => ({
//     shouldShowAlert: true,
//     shouldPlaySound: true,
//     shouldSetBadge: true,
//   }),
// });

// // Function to request notification permissions
// async function requestNotificationPermissions() {
//   const { status } = await Notifications.requestPermissionsAsync();
//   if (status !== 'granted') {
//     alert('Permission to receive notifications was denied');
//     return false;
//   }
//   return true;
// }

// // Function to schedule a sample notification
// async function scheduleSampleNotification() {
//   await Notifications.scheduleNotificationAsync({
//     content: {
//       title: "Secure your Google Account",
//       body: "Check the activity of your account and secure it if necessary.",
//     },
//     trigger: { seconds: 5 }, // Notification will trigger after 5 seconds
//   });
// }

// export default function Index() {
//   useEffect(() => {
//     // Request permissions when the app starts
//     requestNotificationPermissions();

//     // Schedule a sample notification for testing
//     scheduleSampleNotification();
//   }, []);

//   return <Redirect href="/(auth)/SignIn" />;
// }

// const styles = StyleSheet.create({
//   container: {
//     flex: 1,
//   },
// });

import React, { useEffect } from 'react';
import { Redirect } from 'expo-router';
import { StyleSheet } from 'react-native';
import * as Notifications from 'expo-notifications';

// Set up the notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

// Function to request notification permissions
async function requestNotificationPermissions() {
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== 'granted') {
    alert('Permission to receive notifications was denied');
    return false;
  }
  return true;
}

// Function to format date for display
function formatDeadline(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// Function to schedule notifications for an array of task data
async function scheduleTaskNotifications(taskArray) {
  for (const taskData of taskArray) {
    const formattedDeadline = formatDeadline(taskData.deadline);

    await Notifications.scheduleNotificationAsync({
      content: {
        title: taskData.task,
        body: taskData.details,
        data: taskData,
        subtitle: `Deadline: ${formattedDeadline}`,
        categoryIdentifier: taskData.confidence,
        summaryArgument: taskData.source_email_from,
      },
      trigger: { seconds: 5 }, // Notification will trigger after 5 seconds
    });
  }
}

export default function Index() {
  useEffect(() => {
    // Request permissions when the app starts
    requestNotificationPermissions();

    // Sample task data array
    const taskArray = [
      // {
      //   "task": "Secure your Google Account",
      //   "deadline": "2025-04-03T14:15:54+00:00",
      //   "details": "Check the activity of your account and secure it if necessary.",
      //   "confidence": "high",
      //   "source_email_id": "6",
      //   "source_email_subject": "Security alert",
      //   "source_email_from": "Google <no-reply@accounts.google.com>",
      //   "extraction_time": "2025-04-03T19:56:52.841223",
      //   "id": "dl_20250403195652_2208898654208"
      // },
      {
        "task": "Submit quarterly tax report",
        "deadline": "2025-04-15T17:00:00+00:00",
        "details": "The deadline for filing your Q1 tax report is approaching. Please submit all required documentation.",
        "confidence": "high",
        "source_email_id": "12",
        "source_email_subject": "Tax Filing Deadline Reminder",
        "source_email_from": "Tax Department <notifications@taxdept.gov>",
        "extraction_time": "2025-04-03T21:22:45.781902",
        "id": "dl_20250403212245_4508899123456"
      }
    ];

    // Schedule notifications for the task array
    scheduleTaskNotifications(taskArray);
  }, []);

  return <Redirect href="/(auth)/SignIn" />;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
