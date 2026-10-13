// components/ChatMessages.js
import React, { useCallback, useMemo, forwardRef } from 'react';
import { View, FlatList, StyleSheet, Text, Image } from 'react-native';
import RecipeCard from './RecipeCard';
import chinchillaAvatar from '../assets/chinchilla_cook.jpg';


const ChatMessages = forwardRef(({ 
  chat, 
  onShowRecipe, 
  onDeleteRecipe, 
  API_URL,
  onSync 
}, ref) => {

  const listData = useMemo(() => {
    const rows = [];
    for (const msg of chat) {
      rows.push({ type: 'message', key: `msg-${msg.id}`, message: msg });
      (msg.recipes || []).forEach((recipe, index) => {
        rows.push({
          type: 'recipe',
          key: `recipe-${msg.id}-${recipe.id ?? index}`,
          recipe,
        });
      });
    }
    return rows;
  }, [chat]);

  const renderItem = useCallback(({ item }) => {
    if (item.type === 'recipe') {
      return (
        <View style={styles.recipeRow}>
          <RecipeCard
            recipe={item.recipe}
            onPress={onShowRecipe}
            onDelete={onDeleteRecipe}
            API_URL={API_URL}
          />
        </View>
      );
    }

    const { message } = item;
    return (
      <View style={styles.messageContainer}>
        {/* User Message - Right aligned */}
        <View style={styles.userMessage}>
          <View style={styles.userBubble}>
            <Text style={styles.userBubbleText}>{message.user}</Text>
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
            <Text style={styles.botBubbleText}>{message.bot}</Text>
          </View>
        </View>
      </View>
    );
  }, [onShowRecipe, onDeleteRecipe, API_URL]);

  return (
    <FlatList
      ref={ref}
      data={listData}
      keyExtractor={(item) => item.key}
      renderItem={renderItem}
      style={styles.chatList}
      contentContainerStyle={{
        paddingTop: 0,
        paddingBottom: 40,
      }}
      removeClippedSubviews={true}
      initialNumToRender={8}
      maxToRenderPerBatch={10}
      windowSize={15}
      keyboardShouldPersistTaps="handled"
    />
  );
});

const styles = StyleSheet.create({
  messageContainer: {
    marginVertical: 3,
    paddingHorizontal: 12,
  },

  recipeRow: {
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
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 1,
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