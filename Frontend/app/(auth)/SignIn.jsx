import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Image } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';



const SignIn = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  const handleEmailSignIn = () => {
    console.log('Sign in with email:', email);
    router.replace('/(tabs)/Remainder');
  };
  const handleEmailSignUp = () => {
    console.log('Sign in with email:', email);
    router.replace('/(auth)/Remainder');
  };

  const handleGoogleSignIn = () => {
    console.log('Sign in with Google');
    // Implement Google Sign-In logic here
    router.replace('/(tabs)/Remainder');
  };

  return (
    <LinearGradient
      colors={['#FFD700', '#FF8C00', '#FF4500']}
      style={styles.background}
    >
      <View style={styles.container}>
        {/* <Image source={logo} style={styles.logo} /> */}
        <Text style={styles.title}>Welcome Back!</Text>
        
        <View style={styles.inputContainer}>
          <Ionicons name="mail-outline" size={22} color="rgb(133, 72, 54)" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Email"
            placeholderTextColor="rgba(133, 72, 54, 0.6)"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
          />
          
        </View>
        <View style={styles.inputContainer}>
          <Ionicons name="lock-closed" size={22} color="rgb(133, 72, 54)" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Password"
            placeholderTextColor="rgba(133, 72, 54, 0.6)"
            value={password}
            onChangeText={setPassword}
            secureTextEntry={!showPassword}
            autoCapitalize="none"
          />
          <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
            <Ionicons 
              name={showPassword ? "eye-off" : "eye"} 
              size={22} 
              color="rgb(133, 72, 54)" 
            />
          </TouchableOpacity>
        </View>
        
        <TouchableOpacity style={styles.signInButton} onPress={handleEmailSignIn}>
          <Text style={styles.signInButtonText}>Sign In with Email</Text>
        </TouchableOpacity>
        
        <View style={styles.divider}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>OR</Text>
          <View style={styles.dividerLine} />
        </View>
        
        <TouchableOpacity style={styles.googleButton} onPress={handleGoogleSignIn}>
          <Ionicons name="logo-google" size={22} color="rgb(247, 247, 247)" style={styles.googleIcon} />
          <Text style={styles.googleButtonText}>Sign In with Google</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.forgotPassword} onPress={() => console.log('Forgot Password')}>
          <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
        </TouchableOpacity>

        <View style={styles.signUpContainer}>
          <Text style={styles.signUpText}>Don't have an account? </Text>
          <TouchableOpacity onPress={() => router.push('/(auth)/SignUp')}>
            <Text style={styles.signUpButtonText}>Sign Up</Text>
          </TouchableOpacity>
        </View>
      </View>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  background: {
    flex: 1,
  },
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  logo: {
    width: 100,
    height: 100,
    marginBottom: 24,
    borderRadius: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 36,
    color: 'rgb(133, 72, 54)',
    textAlign: 'center',
  },
  inputContainer: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgb(247, 247, 247)',
    borderRadius: 12,
    paddingHorizontal: 16,
    marginBottom: 24,
    height: 56,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: 'rgb(0, 0, 0)',
    height: '100%',
  },
  signInButton: {
    width: '100%',
    height: 56,
    backgroundColor: 'rgb(133, 72, 54)',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.15,
    shadowRadius: 5,
    elevation: 3,
  },
  signInButtonText: {
    color: 'rgb(247, 247, 247)',
    fontSize: 18,
    fontWeight: 'bold',
  },
  divider: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: 'rgba(133, 72, 54, 0.4)',
  },
  dividerText: {
    marginHorizontal: 12,
    color: 'rgb(133, 72, 54)',
    fontWeight: 'bold',
    fontSize: 16,
  },
  googleButton: {
    width: '100%',
    height: 56,
    backgroundColor: 'rgb(0, 0, 0)',
    borderRadius: 12,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.15,
    shadowRadius: 5,
    elevation: 3,
  },
  googleIcon: {
    marginRight: 12,
  },
  googleButtonText: {
    color: 'rgb(247, 247, 247)',
    fontSize: 18,
    fontWeight: 'bold',
  },
  forgotPassword: {
    marginTop: 24,
  },
  forgotPasswordText: {
    color: 'rgb(133, 72, 54)',
    fontSize: 16,
    fontWeight: '500',
    textDecorationLine: 'underline',
  },
  signUpContainer: {
    flexDirection: 'row',
    marginTop: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  signUpText: {
    color: 'rgb(247, 247, 247)',
    fontSize: 16,
  },
  signUpButtonText: {
    color: 'rgb(255, 178, 44)',
    fontSize: 16,
    fontWeight: 'bold',
  },  
});

export default SignIn;
