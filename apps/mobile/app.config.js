const config = {
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
        imageWidth: 320,
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
    package: "com.kpuwal.recipeassistant",
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

  extra: {
    apiUrl: process.env.API_URL,
    eas: {
      projectId: "e40096af-f004-416f-a2ff-9d06c1699873"
    }
  },
};

export default config;