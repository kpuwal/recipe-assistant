if (process.env.EAS_BUILD && !process.env.EXPO_PUBLIC_APP_API_KEY) {
  throw new Error(
    "EXPO_PUBLIC_APP_API_KEY is not set for this EAS build. " +
      "Add it to the EAS environment referenced by eas.json."
  );
}

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
        backgroundColor: "#fbf1d9"
      }
    ],
    ["expo-font",
      {
        fonts: [
          "node_modules/@expo-google-fonts/playfair-display/400Regular/PlayfairDisplay_400Regular.ttf",
          "node_modules/@expo-google-fonts/playfair-display/700Bold/PlayfairDisplay_700Bold.ttf"
        ]
      }
    ],
    [
      "expo-image-picker",
      {
        photosPermission: "Geef toegang tot je foto's om een receptfoto te kiezen.",
        cameraPermission: "Geef toegang tot je camera om een receptfoto te maken.",
        microphonePermission: false
      }
    ],
    "expo-image",
    "expo-status-bar",
    [
      "expo-navigation-bar",
      {
        style: "dark"
      }
    ],
    [
      "expo-audio",
      {
        microphonePermission: false,
        recordAudioAndroid: false,
        enableBackgroundPlayback: false
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