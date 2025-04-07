
// import React from 'react';
// import { View, Text, StyleSheet } from 'react-native';


// export default function Remainder() {
//   return (
//     <View style={styles.container}>
//       <Text>Loading reminders...</Text>
//     </View>
//   );
// }

// const styles = StyleSheet.create({
//   container: {
//     flex: 1,
//     justifyContent: 'center',
//     alignItems: 'center',
//   },
// });


import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  TouchableOpacity, 
  Image,
  ActivityIndicator 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

// Sample data with your JSON structure
const SAMPLE_REMINDERS = [
  {
    "task": "Secure your Google Account",
    "deadline": "2025-04-03T14:15:54+00:00",
    "details": "Check the activity of your account and secure it if necessary.",
    "confidence": "high",
    "source_email_id": "6",
    "source_email_subject": "Security alert",
    "source_email_from": "Google <no-reply@accounts.google.com>",
    "extraction_time": "2025-04-03T19:56:52.841223",
    "id": "dl_20250403195652_2208898654208"
  },
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
  },
]
export default function Remainder() {
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching data
    setTimeout(() => {
      // Add completed property if it doesn't exist
      const processedReminders = SAMPLE_REMINDERS.map(reminder => ({
        ...reminder,
        completed: reminder.completed || false
      }));
      setReminders(processedReminders);
      setLoading(false);
    }, 1000);
  }, []);

  const toggleComplete = (id) => {
    setReminders(reminders.map(reminder => 
      reminder.id === id 
        ? {...reminder, completed: !reminder.completed} 
        : reminder
    ));
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit'
    });
  };

  const getDaysRemaining = (dateString) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const deadline = new Date(dateString);
    deadline.setHours(0, 0, 0, 0);
    
    const diffTime = deadline - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays < 0) return `${Math.abs(diffDays)} days ago`;
    return `${diffDays} days left`;
  };

  const getConfidenceColor = (confidence) => {
    switch(confidence.toLowerCase()) {
      case 'high':
        return '#4CAF50';
      case 'medium':
        return '#FFC107';
      case 'low':
        return '#F44336';
      default:
        return '#757575';
    }
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity 
      style={[
        styles.reminderItem, 
        item.completed && styles.completedItem
      ]}
      onPress={() => toggleComplete(item.id)}
    >
      <View style={styles.reminderContent}>
        <View style={styles.reminderHeader}>
          <View style={styles.sourceContainer}>
            <Text style={styles.sourceText} numberOfLines={1}>
              {item.source_email_from.split('<')[0].trim()}
            </Text>
            <View style={[
              styles.confidenceBadge, 
              {backgroundColor: getConfidenceColor(item.confidence)}
            ]}>
              <Text style={styles.confidenceText}>{item.confidence}</Text>
            </View>
          </View>
          <Text style={[
            styles.reminderTask, 
            item.completed && styles.completedText
          ]}>
            {item.task}
          </Text>
        </View>
        
        <Text style={styles.reminderDetails}>{item.details}</Text>
        
        <View style={styles.reminderFooter}>
          <Text style={styles.reminderDate}>
            <Ionicons name="time-outline" size={14} color="#666" />
            {' '}{formatDate(item.deadline)}
          </Text>
          <Text style={[
            styles.reminderDaysLeft,
            getDaysRemaining(item.deadline).includes('ago') && styles.overdue
          ]}>
            {getDaysRemaining(item.deadline)}
          </Text>
        </View>
        
        <View style={styles.emailInfo}>
          <Text style={styles.emailSubject}>
            <Ionicons name="mail-outline" size={12} color="#666" />
            {' '}{item.source_email_subject}
          </Text>
        </View>
      </View>
      
      <TouchableOpacity 
        style={[
          styles.checkButton,
          item.completed && styles.completedCheckButton
        ]}
        onPress={() => toggleComplete(item.id)}
      >
        <Ionicons 
          name={item.completed ? "checkmark-circle" : "ellipse-outline"} 
          size={24} 
          color={item.completed ? "#4CAF50" : "#ccc"} 
        />
      </TouchableOpacity>
    </TouchableOpacity>
  );

  const renderEmptyList = () => (
    <View style={styles.emptyContainer}>
      <Image 
        source={require('../../assets/noremain.png')} 
        style={styles.emptyImage} 
      />
      <Text style={styles.emptyTitle}>No Reminders</Text>
      <Text style={styles.emptyText}>
        You don't have any upcoming deadlines. 
        Check back after scanning your emails.
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#FFB22C', 'rgb(133, 72, 54)']}
        start={{x: 0, y: 0}}
        end={{x: 1, y: 0.2}}
        style={styles.header}
      >
        <Text style={styles.headerTitle}>Upcoming Deadlines</Text>
        <Text style={styles.headerSubtitle}>
          {reminders.filter(r => !r.completed).length} active reminders
        </Text>
      </LinearGradient>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FFB22C" />
          <Text style={styles.loadingText}>Loading reminders...</Text>
        </View>
      ) : (
        <FlatList
          data={reminders.sort((a, b) => new Date(a.deadline) - new Date(b.deadline))}
          renderItem={renderItem}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.listContainer}
          ListEmptyComponent={renderEmptyList}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7f7f7',
  },
  header: {
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  listContainer: {
    padding: 16,
    paddingTop: 20,
    flexGrow: 1,
  },
  reminderItem: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  completedItem: {
    backgroundColor: '#f5f5f5',
    opacity: 0.8,
  },
  reminderContent: {
    flex: 1,
  },
  reminderHeader: {
    marginBottom: 8,
  },
  sourceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  sourceText: {
    fontSize: 12,
    color: '#666',
    flex: 1,
  },
  confidenceBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    marginLeft: 8,
  },
  confidenceText: {
    fontSize: 10,
    color: 'white',
    fontWeight: 'bold',
  },
  reminderTask: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  completedText: {
    textDecorationLine: 'line-through',
    color: '#888',
  },
  reminderDetails: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  reminderFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  reminderDate: {
    fontSize: 13,
    color: '#666',
  },
  reminderDaysLeft: {
    fontSize: 13,
    fontWeight: '500',
    color: '#FFB22C',
  },
  overdue: {
    color: '#f44336',
  },
  emailInfo: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 8,
  },
  emailSubject: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic',
  },
  checkButton: {
    padding: 8,
  },
  completedCheckButton: {
    opacity: 0.8,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
    paddingVertical: 100,
  },
  emptyImage: {
    width: 100,
    height: 100,
    marginBottom: 20,
    opacity: 0.7,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 22,
  },
});
