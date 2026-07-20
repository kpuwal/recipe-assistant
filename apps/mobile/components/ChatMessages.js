// components/ChatMessages.js
import React, { useCallback, forwardRef } from 'react';
import { View, FlatList, StyleSheet, Text, Image } from 'react-native';
import RecipeCard from './RecipeCard';
import CheatSheet from './CheatSheet';
import chinchillaAvatar from '../assets/chinchilla_cook.jpg';


const ChatMessages = forwardRef(({ 
  chat, 
  onShowRecipe, 
  onDeleteRecipe, 
  API_URL,
  onSync 
}, ref) => {

  const renderItem = useCallback(({ item }) => (
    <View style={styles.messageContainer}>
      {/* User Message - Right aligned */}
      <View style={styles.userMessage}>
        <View style={styles.userBubble}>
          <Text style={styles.userBubbleText}>{item.user}</Text>
        </View>
      </View>

      {/* Bot Message - Avatar + Bubble */}
      <View style={styles.botMessage}>
        <Image 
          source={chinchillaAvatar} 
          style={styles.botAvatar}
          resizeMode="cover"
        />
        
        <View style={styles.botBubble}>
          <Text style={styles.botBubbleText}>{item.bot}</Text>
        </View>
      </View>

      {item.recipes?.map((recipe) => (
        <RecipeCard 
          key={recipe.id} 
          recipe={recipe} 
          onPress={onShowRecipe}
          onDelete={onDeleteRecipe}
          API_URL={API_URL}
        />
      ))}
    </View>
  ), [onShowRecipe, onDeleteRecipe, API_URL]);

  if (chat.length === 0) {
    return <CheatSheet onSync={onSync} />;
  }

  return (
    <FlatList
      ref={ref}
      data={chat}
      keyExtractor={(item, index) => `chat-${index}`}
      renderItem={renderItem}
      style={styles.chatList}
      contentContainerStyle={{
        paddingTop: 20,
        paddingBottom: 40,
      }}
      removeClippedSubviews={true}
      initialNumToRender={6}
      maxToRenderPerBatch={10}
      windowSize={15}
      keyboardShouldPersistTaps="handled"
    />
  );
});

const styles = StyleSheet.create({
  messageContainer: {
    marginVertical: 8,
    paddingHorizontal: 12,
  },

  /* User Message */
  userMessage: {
    alignItems: 'flex-end',
    marginBottom: 4,
  },
  userBubble: {
    backgroundColor: "#e74c3c",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
    borderBottomRightRadius: 4,
    maxWidth: "82%",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  userBubbleText: {
    color: "#ffffff",
    fontSize: 16,
    lineHeight: 22,
  },

  /* Bot Message */
  botMessage: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 4,
  },
  botAvatar: {
    width: 36,
    height: 46,
    // borderRadius: 18,
    marginRight: 8,
    marginTop: 2,
  },
  botBubble: {
    backgroundColor: "#f0f0f0",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
    borderBottomLeftRadius: 4,
    maxWidth: "75%",           // Slightly smaller to leave space for avatar
  },
  botBubbleText: {
    color: "#1a1a1a",
    fontSize: 16,
    lineHeight: 22,
  },

  chatList: {
    flex: 1,
  },
});

export default ChatMessages;