import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Image,
  KeyboardAvoidingView,
  Platform,
  Alert,
  StyleSheet,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import axios from "axios";

import { useFonts } from 'expo-font';
import { 
  PlayfairDisplay_400Regular,
  PlayfairDisplay_700Bold 
} from '@expo-google-fonts/playfair-display';

import Header from "./components/Header";
import TagFilters from "./components/TagFilters";
import ChatMessages from "./components/ChatMessages";
import InputArea from "./components/InputArea";
import LoadingOverlay from "./components/LoadingOverlay"

import RecipeModal from "./modals/RecipeModal";
import EditRecipeModal from "./modals/EditRecipeModal";
import AddRecipeModal from "./modals/AddRecipeModal";
import SyncResultModal from "./modals/SyncResultModal";

import { useChat } from './hooks/useChat';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.apiUrl;

if (!API_URL) {
  throw new Error('EXPO_PUBLIC_API_URL is missing. Check your .env file.');
}


export default function App() {
  const [fontsLoaded] = useFonts({
    PlayfairRegular: PlayfairDisplay_400Regular,
    PlayfairBold: PlayfairDisplay_700Bold,
  });

  const {
    message,
    setMessage,
    chat,
    activeTag,
    isLoading: chatLoading,
    chatListRef,
    clearAll,
    searchByTag,
    sendMessage,
    deleteRecipe,
  } = useChat("nl");

  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [syncResult, setSyncResult] = useState(null);
  const [showSplash, setShowSplash] = useState(true);

  useEffect(() => {
    if (fontsLoaded) {
      const timer = setTimeout(() => setShowSplash(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [fontsLoaded]);

  const handleFavoriteChanged = useCallback((updatedRecipe) => {
    setSelectedRecipe(updatedRecipe);
  }, []);

  const handleRecipeUpdated = useCallback((updatedRecipe) => {
    setSelectedRecipe(updatedRecipe);
  }, []);

  const syncRecipes = useCallback(async () => {
    try {
      const response = await axios.post(`${API_URL}/ingestion/sync-recipes`);
      const summary = response.data.summary;
      setSyncResult(summary);
    } catch (error) {
      console.error("Sync error:", error);
      Alert.alert(
        "Sync fout",
        error?.response?.data?.detail || "Kon recepten niet synchroniseren."
      );
    }
  }, []);

  const showRecipe = useCallback(async (recipe) => {
    if (recipe.source === "ai") {
      setSelectedRecipe(recipe);
      setModalVisible(true);
      return;
    }
    try {
      const response = await axios.get(`${API_URL}/recipes/${recipe.id}`, {
        params: { lang: "nl" },
      });
      setSelectedRecipe(response.data);
      setModalVisible(true);
    } catch (error) {
      console.log(error);
      Alert.alert("Fout", "Kon recept niet laden.");
    }
  }, []);

  if (!fontsLoaded || showSplash) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#f4f4f4" }}>
        <Image 
          source={require("./assets/splash.jpg")} 
          style={{ width: 320, height: 320 }} 
          resizeMode="contain" 
        />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === "ios" ? "padding" : "height"}
      >
        <Header />
        
        <TagFilters 
          activeTag={activeTag}
          onTagPress={searchByTag}
          onAddRecipe={() => setAddModalVisible(true)}
          onClear={clearAll}
        />

        <ChatMessages
          ref={chatListRef}
          chat={chat}
          onShowRecipe={showRecipe}
          onDeleteRecipe={deleteRecipe}
          API_URL={API_URL}
          onSync={syncRecipes}
        />

        <InputArea 
          message={message}
          setMessage={setMessage}
          onSend={sendMessage}
          isLoading={chatLoading}
        />
      </KeyboardAvoidingView>

      <RecipeModal
        visible={modalVisible && !!selectedRecipe}
        recipe={selectedRecipe}
        language="nl"
        api_url={API_URL}
        onClose={() => {
          setModalVisible(false);
          setTimeout(() => setSelectedRecipe(null), 300);
        }}
        onFavoriteChanged={handleFavoriteChanged}
        onEditPress={(recipeToEdit) => {
          setModalVisible(false);
          setTimeout(() => {
            setSelectedRecipe(recipeToEdit);
            setEditModalVisible(true);
          }, 350);
        }}
      />

      <EditRecipeModal
        visible={editModalVisible && !!selectedRecipe}
        recipe={selectedRecipe}
        api_url={API_URL}
        onClose={() => {
          setEditModalVisible(false);
          setTimeout(() => setSelectedRecipe(null), 300);
        }}
        onRecipeUpdated={handleRecipeUpdated}
      />

      <AddRecipeModal
        visible={addModalVisible}
        onClose={() => setAddModalVisible(false)}
        api_url={API_URL}
        onRecipeAdded={() => {
          Alert.alert("Succes", "Recept succesvol toegevoegd!");
        }}
      />

      <SyncResultModal
        result={syncResult}
        onClose={() => setSyncResult(null)}
      />
      {chatLoading && <LoadingOverlay />}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: "#FAFAFA" },
  container: { flex: 1 },
});