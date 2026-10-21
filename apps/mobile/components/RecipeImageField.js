import React from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from "react-native";
import { Image } from "expo-image";
import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";

const PICKER_OPTIONS = {
  mediaTypes: ["images"],
  allowsEditing: true,
  aspect: [4, 3],
  quality: 0.8,
  preferredAssetRepresentationMode:
    ImagePicker.UIImagePickerPreferredAssetRepresentationMode.Compatible,
};

const RecipeImageField = ({
  imageAsset,
  existingImage,
  onChange,
  onRemove,
}) => {
  const previewSource = imageAsset
    ? { uri: imageAsset.uri }
    : existingImage || null;

  const pickFromLibrary = async () => {
    try {
      const permission =
        await ImagePicker.requestMediaLibraryPermissionsAsync();

      if (!permission.granted) {
        Alert.alert(
          "Toegang nodig",
          "Geef toegang tot je foto's om een receptfoto te kiezen."
        );
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync(
        PICKER_OPTIONS
      );

      if (!result.canceled) {
        onChange(result.assets[0]);
      }
    } catch (error) {
      console.error("Pick image error:", error);
      Alert.alert("Fout", "Kon geen foto kiezen.");
    }
  };

  const takePhoto = async () => {
    try {
      const permission = await ImagePicker.requestCameraPermissionsAsync();

      if (!permission.granted) {
        Alert.alert(
          "Toegang nodig",
          "Geef toegang tot je camera om een receptfoto te maken."
        );
        return;
      }

      const result = await ImagePicker.launchCameraAsync(PICKER_OPTIONS);

      if (!result.canceled) {
        onChange(result.assets[0]);
      }
    } catch (error) {
      console.error("Camera image error:", error);
      Alert.alert("Fout", "Kon geen foto maken.");
    }
  };

  return (
    <View style={styles.container}>
      {previewSource ? (
        <View style={styles.previewWrap}>
          <Image
            source={previewSource}
            style={styles.preview}
            contentFit="cover"
            transition={150}
          />
          <TouchableOpacity
            style={styles.removeButton}
            onPress={onRemove}
            hitSlop={8}
          >
            <Ionicons name="close" size={16} color="#fff" />
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.placeholder}>
          <Ionicons name="image-outline" size={32} color="#999" />
          <Text style={styles.placeholderText}>Nog geen foto</Text>
        </View>
      )}

      <View style={styles.actions}>
        <TouchableOpacity style={styles.action} onPress={pickFromLibrary}>
          <Ionicons name="images-outline" size={18} color="#e74c3c" />
          <Text style={styles.actionText}>Galerij</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.action} onPress={takePhoto}>
          <Ionicons name="camera-outline" size={18} color="#e74c3c" />
          <Text style={styles.actionText}>Camera</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    gap: 10,
    marginBottom: 12,
  },
  previewWrap: {
    position: "relative",
  },
  preview: {
    width: "100%",
    height: 180,
    borderRadius: 12,
    backgroundColor: "#eee",
  },
  removeButton: {
    position: "absolute",
    top: 8,
    right: 8,
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(0, 0, 0, 0.6)",
  },
  placeholder: {
    width: "100%",
    height: 140,
    borderRadius: 12,
    borderWidth: 1,
    borderStyle: "dashed",
    borderColor: "#ddd",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#fafafa",
    gap: 6,
  },
  placeholderText: {
    color: "#999",
    fontSize: 14,
  },
  actions: {
    flexDirection: "row",
    gap: 8,
  },
  action: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#f5c6c2",
    backgroundColor: "#fdecea",
  },
  actionText: {
    color: "#e74c3c",
    fontWeight: "600",
    fontSize: 14,
  },
});

export default RecipeImageField;
