import { ExpoConfig } from 'expo/config';

const config: ExpoConfig = {
  name: "RecipeAssistantApp",
  slug: "RecipeAssistantApp",
  version: "1.0.0",
  orientation: "portrait",
  icon: "./assets/icon.png",
  userInterfaceStyle: "light",
  newArchEnabled: true,

  plugins: [
    [
      "expo-splash-screen",
      {
        image: "./assets/splash.jpg",
        imageWidth: 220,
        resizeMode: "contain",
        backgroundColor: "#FAFAFA"
      }
    ],
    "expo-font"
  ],

  ios: {
    supportsTablet: true
  },

  android: {
    softwareKeyboardLayoutMode: "resize",
    adaptiveIcon: {
      foregroundImage: "./assets/adaptive-icon.png",
      backgroundColor: "#ffffff"
    },
    edgeToEdgeEnabled: true
  },

  web: {
    favicon: "./assets/favicon.png"
  },

  // Environment variables go here
  extra: {
    apiUrl: process.env.EXPO_PUBLIC_API_URL,
  },
};

export default config;