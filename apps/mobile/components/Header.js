import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import chinchillaLogo from '../assets/cookbook-logo2.png';

const Header = () => {
  return (
    <View style={styles.header}>
        <View style={styles.logoContainer}>
        <Image source={chinchillaLogo} style={styles.logoImage} resizeMode="contain" />
        <View style={styles.logoTextContainer}>
            <Text style={[styles.logoText, { fontFamily: 'PlayfairBold' }]}>Chill Chinchilla Cookbook</Text>
            <Text style={styles.subtitle}>Zoek op ingrediënten, categorie of kooktijd</Text>
        </View>
        </View>
    </View>
  );
};

const styles = StyleSheet.create({
    header: { paddingHorizontal: 10, paddingTop: 10, paddingBottom: 8, backgroundColor: "#ffffff", borderBottomWidth: 1, borderBottomColor: "#eee" },
    logoContainer: { flexDirection: "row", alignItems: "flex-start" },
    logoImage: { width: 90, height: 124, marginRight: 14, borderRadius: 14 },
    logoTextContainer: { flex: 1, justifyContent: "center", paddingTop: 15 },
    logoText: { fontSize: 32, fontWeight: "700", color: "#1a1a1a", marginBottom: 4 },
    subtitle: { fontSize: 14.5, color: "#666", lineHeight: 16 },
})

export default Header;