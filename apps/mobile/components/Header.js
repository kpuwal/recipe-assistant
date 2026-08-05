import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import chinchillaLogo from '../assets/cookbook-logo2.png';

const Header = () => {
  return (
    <View style={styles.header}>
      <View style={styles.logoContainer}>
        <Image
          source={chinchillaLogo}
          style={styles.logoImage}
          resizeMode="contain"
        />
        <View style={styles.logoTextContainer} pointerEvents="none">
          <Text style={styles.logoText}>Chill Chinchilla</Text>
          <Text style={styles.cookbookText}>Cookbook</Text>
          <Text style={styles.subtitle}>
            Zoek op ingrediënten, categorie of kooktijd
          </Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  header: {
    paddingHorizontal: 16,
    paddingTop: 28,
    paddingBottom: 14,
    backgroundColor: "#ffffff",
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  logoContainer: {
    flexDirection: "row",
    alignItems: "center",
  },
  logoImage: {
    width: 80,
    height: 98,
    marginRight: 14,
    borderRadius: 12,
  },
  logoTextContainer: {
    flex: 1,
    justifyContent: "center",
  },
  logoText: {
    fontFamily: "PlayfairBold",
    fontSize: 29,
    color: "#1a1a1a",
    lineHeight: 30,
    includeFontPadding: false,
  },
  cookbookText: {
    fontFamily: "PlayfairRegular",
    fontSize: 20,
    color: "#e74c3c",
    lineHeight: 22,
    letterSpacing: 0.3,
    marginTop: -2,
    marginBottom: 4,
    includeFontPadding: false,
  },
  subtitle: {
    fontFamily: "PlayfairRegular",
    fontSize: 14,
    color: "#999",
    lineHeight: 18,
    includeFontPadding: false,
  },
});

export default Header;
