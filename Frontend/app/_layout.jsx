// app/_layout.js
import { Stack } from 'expo-router';
import { StatusBar, View, StyleSheet, Text } from 'react-native'; // Import Text

export default function Layout() {
  return (
    <View style={styles.container}>
      <StatusBar hidden={true} />
      <Stack screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: 'white' },
      }}>
        <Stack.Screen name="(auth)" />
        <Stack.Screen name="(tabs)" />
      </Stack>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});