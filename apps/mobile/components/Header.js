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

        <View style={styles.logoTextContainer}>
          <View style={styles.textBlock}>
            <Text style={styles.logoText}>Chill Chinchilla</Text>
            <Text style={styles.cookbookText}>Cookbook</Text>
          </View>

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
    paddingHorizontal: 12,
    paddingTop: 12,
    paddingBottom: 10,
    backgroundColor: "#ffffff",
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  logoContainer: {
    flexDirection: "row",
    alignItems: "flex-start",
  },
  logoImage: {
    width: 85,
    height: 110,
    marginRight: 14,
    borderRadius: 14,
  },
  logoTextContainer: {
    flex: 1,
    justifyContent: "center",
    marginTop: 15,
  },
  textBlock: {
    alignSelf: "flex-start",     // Important: shrinks to content width
  },
  logoText: {
    fontFamily: "PlayfairBold",
    fontSize: 31,
    color: "#1a1a1a",
    marginBottom: 4,
  },
  cookbookText: {
    fontFamily: "PlayfairBold",
    fontSize: 36,
    color: "#1a1a1a",
    alignSelf: "center",         // Now centers relative to "Chill Chinchilla"
    marginTop: -10,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14.5,
    color: "#666",
    lineHeight: 17,
    marginTop: 4,
  },
});

export default Header;