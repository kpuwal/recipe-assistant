import React from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet } from 'react-native';

const InputArea = ({ message, setMessage, onSend, isLoading }) => {
  return (
    <View style={styles.inputContainer}>
      <TextInput 
        style={styles.input} 
        value={message} 
        onChangeText={setMessage} 
        placeholder="Vraag om recepten..." 
        placeholderTextColor="#888" 
        multiline 
      />
      <TouchableOpacity 
        style={styles.sendButton} 
        onPress={onSend} 
        activeOpacity={0.8}
        disabled={isLoading}
      >
        <Text style={styles.sendButtonText}>↑</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  inputContainer: { 
    flexDirection: "row", 
    alignItems: "flex-end", 
    paddingHorizontal: 12, 
    paddingVertical: 10, 
    borderTopWidth: 1, 
    borderTopColor: "#eee", 
    backgroundColor: "#fff" 
  },
  input: { 
    flex: 1, 
    backgroundColor: "#ffffff", 
    borderWidth: 1, 
    borderColor: "#ddd", 
    borderRadius: 20, 
    paddingHorizontal: 16, 
    paddingVertical: 12, 
    marginRight: 10, 
    maxHeight: 120, 
    fontSize: 16, 
    lineHeight: 22 
  },
  sendButton: { 
    width: 48, 
    height: 48, 
    borderRadius: 999, 
    backgroundColor: "#e74c3c", 
    justifyContent: "center", 
    alignItems: "center", 
    shadowColor: "#e74c3c", 
    shadowOffset: { width: 0, height: 3 }, 
    shadowOpacity: 0.3, 
    shadowRadius: 5, 
    elevation: 6 
  },
  sendButtonText: { 
    fontSize: 22, 
    color: "#fff", 
    fontWeight: "bold", 
    lineHeight: 24, 
    marginTop: -2 
  },
});

export default InputArea;