import React, { useState, useCallback } from "react";
import {
  KeyboardAvoidingView,
  Platform,
  Alert,
  StyleSheet,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

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
import { API_URL, apiService } from './services/api';

export default function App() {
  const [fontsLoaded] = useFonts({
    PlayfairRegular: PlayfairDisplay_400Regular,
    PlayfairBold: PlayfairDisplay_700Bold,
  });

  const [showError, setShowError] = useState(false);

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

  const handleFavoriteChanged = useCallback((updatedRecipe) => {
    setSelectedRecipe(updatedRecipe);
  }, []);

  const handleRecipeUpdated = useCallback((updatedRecipe) => {
    setSelectedRecipe(updatedRecipe);
  }, []);

const syncRecipes = useCallback(async () => {
  try {
    const response = await apiService.syncRecipes();
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
    const response = await apiService.getRecipe(recipe.id, "nl");
    setSelectedRecipe(response.data);
    setModalVisible(true);
  } catch (error) {
    console.log(error);
    Alert.alert("Fout", "Kon recept niet laden.");
  }
}, []);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>

        <Header />

        <TagFilters
          activeTag={activeTag}
          onTagPress={searchByTag}
          onAddRecipe={() => setAddModalVisible(true)}
          onClear={clearAll}
        />

        {/* Chat / CheatSheet occupies the remaining screen */}
        <View style={styles.chatContainer}>
          <ChatMessages
            ref={chatListRef}
            chat={chat}
            onShowRecipe={showRecipe}
            onDeleteRecipe={deleteRecipe}
            API_URL={API_URL}
            onSync={syncRecipes}
          />
        </View>

        {/* Input sits independently above the keyboard */}
        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : "height"}
        >
          <InputArea
            message={message}
            setMessage={setMessage}
            onSend={sendMessage}
            isLoading={chatLoading}
          />
        </KeyboardAvoidingView>

      </View>

<RecipeModal
  visible={modalVisible && !!selectedRecipe}
  recipe={selectedRecipe}
  language="nl"
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
          Alert.alert(
            "Succes",
            "Recept succesvol toegevoegd!"
          );
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
  safeArea: {
    flex: 1,
    backgroundColor: "#FAFAFA",
  },

  container: {
    flex: 1,
  },

  chatContainer: {
    flex: 1,
  },

  // inputWrapper: {
  //   position: "absolute",
  //   left: 0,
  //   right: 0,
  //   bottom: 0,
  // },

  splashContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#f4f4f4",
  },

  splashImage: {
    width: 320,
    height: 320,
  },
});