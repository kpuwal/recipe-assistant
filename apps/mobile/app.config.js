const config = {
  name: "RecipeAssistantApp",
  slug: "RecipeAssistantApp",
  version: "1.0.0",
  orientation: "portrait",
  icon: "./assets/icon.png",
  userInterfaceStyle: "light",

  plugins: [
    [
      "expo-splash-screen",
      {
        image: "./assets/splash.jpg",
        imageWidth: 320,
        resizeMode: "contain",
        backgroundColor: "#fafafa"
      }
    ],
    ["expo-font",
      {
        fonts: [
          "node_modules/@expo-google-fonts/playfair-display/400Regular/PlayfairDisplay_400Regular.ttf",
          "node_modules/@expo-google-fonts/playfair-display/700Bold/PlayfairDisplay_700Bold.ttf"
        ]
      }
    ]
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
    },

  web: {
    favicon: "./assets/favicon.png"
  },

  extra: {
    apiUrl: process.env.EXPO_PUBLIC_API_URL,
    eas: {
      projectId: "e40096af-f004-416f-a2ff-9d06c1699873"
    }
  },
};

export default config;