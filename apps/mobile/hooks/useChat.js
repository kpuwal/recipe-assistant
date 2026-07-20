// hooks/useChat.js
import { useState, useRef, useCallback, useEffect } from 'react';
import { Keyboard, Alert } from 'react-native';
import axios from 'axios';

const API_URL = "http://192.168.2.7:8000";

export const useChat = (language = "nl") => {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [activeTag, setActiveTag] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const chatListRef = useRef(null);

  useEffect(() => {
    if (chat.length === 0) return;
    requestAnimationFrame(() => {
      chatListRef.current?.scrollToOffset({ offset: 0, animated: true });
    });
  }, [chat]);

  const clearAll = useCallback(() => {
    setChat([]);
    setActiveTag(null);
  }, []);

  const scrollToTop = useCallback(() => {
    chatListRef.current?.scrollToOffset({ offset: 0, animated: true });
  }, []);

  const searchByTag = useCallback(async (tag) => {
    setActiveTag(tag.label);
    
    try {
      setIsLoading(true);
      let response;

      if (tag.query === "favorieten") {
        response = await axios.get(`${API_URL}/recipes?favorites_only=true`);
        
        setChat((prev) => [
          {
            user: `Snelzoeken: ${tag.label}`,
            bot: `${response.data.length || 0} favoriete recepten gevonden.`,
            recipes: response.data || [],
          },
          ...prev,
        ]);
      } else {
        response = await axios.get(`${API_URL}/recipes/search`, {
          params: { q: tag.query },
        });

        const recipeCount = response.data.length || 0;
        
        setChat((prev) => [
          {
            user: `Snelzoeken: ${tag.label}`,
            bot: recipeCount > 0 
              ? `${recipeCount} recepten gevonden.` 
              : "Geen recepten gevonden voor deze zoekopdracht.",
            recipes: response.data || [],
          },
          ...prev,
        ]);
      }
    } catch (error) {
      console.error("Tag search error:", error);
      Alert.alert("Fout", "Kon niet zoeken. Probeer het opnieuw.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendMessage = useCallback(async () => {
    if (!message.trim()) return;

    Keyboard.dismiss();
    try {
      setIsLoading(true);
      const response = await axios.post(`${API_URL}/chat`, {
        message,
        language,
      });

      setChat((prev) => [
        {
          user: message,
          bot: response.data.answer,
          recipes: response.data.recipes || [],
        },
        ...prev,
      ]);
      setMessage("");
    } catch (error) {
      console.log(error);
      Alert.alert(
        "Fout", 
        error?.response?.data ? JSON.stringify(error.response.data) : error.message
      );
    } finally {
      setIsLoading(false);
    }
  }, [message, language]);

  const deleteRecipe = useCallback(async (recipeId) => {
    Alert.alert(
      "Recept verwijderen",
      "Weet je zeker dat je dit recept wilt verwijderen?",
      [
        { text: "Annuleren", style: "cancel" },
        {
          text: "Verwijderen",
          style: "destructive",
          onPress: async () => {
            try {
              await axios.delete(`${API_URL}/recipes/${recipeId}`);
              setChat((prev) =>
                prev.map((msg) => ({
                  ...msg,
                  recipes: msg.recipes?.filter((r) => r.id !== recipeId),
                }))
              );
            } catch (err) {
              Alert.alert("Fout", "Kon recept niet verwijderen.");
            }
          },
        },
      ]
    );
  }, []);

  return {
    // State
    message,
    setMessage,
    chat,
    activeTag,
    isLoading,
    chatListRef,

    // Actions
    clearAll,
    searchByTag,
    sendMessage,
    deleteRecipe,
    scrollToTop,
  };
};