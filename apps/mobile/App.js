import React, { useState, useCallback, useEffect } from "react";
import {
  KeyboardAvoidingView,
  Platform,
  Alert,
  StyleSheet,
  View,
  Image,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import * as SplashScreen from "expo-splash-screen";
import {
  useFonts,
  PlayfairDisplay_400Regular,
  PlayfairDisplay_700Bold,
} from "@expo-google-fonts/playfair-display";

import Header from "./components/Header";
import ActionBar from "./components/ActionBar";
import TagFilters from "./components/TagFilters";
import ChatMessages from "./components/ChatMessages";
import InputArea from "./components/InputArea";
import LoadingOverlay from "./components/LoadingOverlay"
import CheatSheet from "./components/CheatSheet";

import RecipeModal from "./modals/RecipeModal";
import EditRecipeModal from "./modals/EditRecipeModal";
import AddRecipeModal from "./modals/AddRecipeModal";
import SyncResultModal from "./modals/SyncResultModal";
import HistoryModal from "./modals/HistoryModal";

import { useChat } from './hooks/useChat';
import { API_URL, apiService } from './services/api';
import TimerOverlay from './components/timers/TimerOverlay';

SplashScreen.setOptions({ duration: 250, fade: true });
SplashScreen.preventAutoHideAsync().catch(() => {});

export default function App() {
  const [showError, setShowError] = useState(false);
  const [splashImageLoaded, setSplashImageLoaded] = useState(false);
  const [warmupDone, setWarmupDone] = useState(false);

  const [fontsLoaded, fontError] = useFonts({
    PlayfairBold: PlayfairDisplay_700Bold,
    PlayfairRegular: PlayfairDisplay_400Regular,
  });

  useEffect(() => {
    if (!splashImageLoaded) return;
    SplashScreen.hideAsync().catch(() => {});
  }, [splashImageLoaded]);

  useEffect(() => {
    let active = true;
    const timeout = setTimeout(() => {
      if (active) setWarmupDone(true);
    }, 8000);

    apiService.warmup()
      .catch(() => {})
      .finally(() => {
        if (!active) return;
        clearTimeout(timeout);
        setWarmupDone(true);
      });

    return () => {
      active = false;
      clearTimeout(timeout);
    };
  }, []);

  const {
    message,
    setMessage,
    chat,
    activeFilter,
    isLoading: chatLoading,
    chatListRef,
    clearAll,
    applyFilter,
    sendMessage,
    deleteRecipe,
  } = useChat("nl");

  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [syncResult, setSyncResult] = useState(null);
  const [historyVisible, setHistoryVisible] = useState(false);

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
    if (!recipe.id) {
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

  const openRecipeFromHistory = useCallback(
    (entry) => {
      setHistoryVisible(false);
      showRecipe({
        id: entry.recipe_id,
        source: entry.source,
        image: entry.image,
        title: entry.title,
      });
    },
    [showRecipe]
  );

  const fontsReady = fontsLoaded || !!fontError;
  const appReady = fontsReady && warmupDone && splashImageLoaded;

  if (!appReady) {
    return (
      <View style={styles.bootSplash}>
        <Image
          source={require("./assets/splash-screen-fullscreen.png")}
          style={styles.bootSplashImage}
          resizeMode="cover"
          onLoad={() => setSplashImageLoaded(true)}
          onError={() => setSplashImageLoaded(true)}
        />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>

        <Header />

        <ActionBar
          onClear={clearAll}
          onSync={syncRecipes}
          onHistory={() => setHistoryVisible(true)}
        />

        <TagFilters
          activeFilter={activeFilter}
          onFilterPress={applyFilter}
          onAddRecipe={() => setAddModalVisible(true)}
        />

        <KeyboardAvoidingView
          style={{ flex: 1 }}
          behavior={Platform.OS === "ios" ? "padding" : "height"}
        >
          <View style={{ flex: 1 }}>
            {chat.length === 0 ? (
              <CheatSheet />
            ) : (
              <ChatMessages
                ref={chatListRef}
                chat={chat}
                onShowRecipe={showRecipe}
                onDeleteRecipe={deleteRecipe}
                API_URL={API_URL}
                onSync={syncRecipes}
              />
            )}
            <InputArea
              message={message}
              setMessage={setMessage}
              onSend={sendMessage}
              isLoading={chatLoading}
            />
          </View>
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
        onCookedChanged={handleFavoriteChanged}
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
        onClose={() => {
          setEditModalVisible(false);
          setTimeout(() => setSelectedRecipe(null), 300);
        }}
        onRecipeUpdated={handleRecipeUpdated}
      />

      <AddRecipeModal
        visible={addModalVisible}
        onClose={() => setAddModalVisible(false)}
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

      <HistoryModal
        visible={historyVisible}
        onClose={() => setHistoryVisible(false)}
        onSelectRecipe={openRecipeFromHistory}
      />

      {chatLoading && <LoadingOverlay />}

      <TimerOverlay />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  bootSplash: {
    flex: 1,
    backgroundColor: "#fbf1d9",
  },

  bootSplashImage: {
    flex: 1,
    width: "100%",
    height: "100%",
  },

  safeArea: {
    flex: 1,
    backgroundColor: "#fafafa",
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
