import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  View,
  Text,
  Modal,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Alert,
  TextInput,
} from "react-native";
import { Image } from "expo-image";
import { Ionicons, Entypo, MaterialIcons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import apiService, { buildRecipeImageUrl } from "../services/api";
import { useTimers } from "../hooks/useTimers";
import TimerOverlay from "../components/timers/TimerOverlay";
import {
  TIMER_ICONS,
  TIMER_ICON_KEYS,
  getOvenModeIcon,
} from "../assets/icons";
import {
  TIMER_COLORS,
  DEFAULT_TIMER_COLOR,
  getTimerColor,
} from "../constants/timerColors";
import { todayISO } from "../utils/dates";

const TIMER_CHIP_COLOR = getTimerColor(DEFAULT_TIMER_COLOR);

const RecipeModal = ({ visible, recipe, onClose, onFavoriteChanged, onCookedChanged, onEditPress, onRecipeSaved }) => {
  const [isFavorite, setIsFavorite] = useState(false);
  const [displayRecipe, setDisplayRecipe] = useState(null);
  const [selectedPersons, setSelectedPersons] = useState(4);
  const [loading, setLoading] = useState(false);
  const [scaling, setScaling] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showTimerForm, setShowTimerForm] = useState(false);
  const [timerStepIndex, setTimerStepIndex] = useState(null);
  const [timerLabel, setTimerLabel] = useState("");
  const [timerMinutes, setTimerMinutes] = useState("5");
  const [timerIcon, setTimerIcon] = useState(null);
  const [timerColor, setTimerColor] = useState(DEFAULT_TIMER_COLOR);
  const [savingTimer, setSavingTimer] = useState(false);
  const [pendingDeleteTimerId, setPendingDeleteTimerId] = useState(null);
  const [markingCooked, setMarkingCooked] = useState(false);

  const { startTimer } = useTimers();
  const insets = useSafeAreaInsets();

  const today = todayISO();
  const isCookedToday = (displayRecipe?.cooked_dates || []).includes(today);

  const scrollViewRef = useRef(null);
  const timerFormY = useRef(0);
  const recipeIdRef = useRef(null);

  const scrollToTimerForm = useCallback(() => {
    requestAnimationFrame(() => {
      scrollViewRef.current?.scrollTo({
        y: Math.max(0, timerFormY.current - 12),
        animated: true,
      });
    });
  }, []);

  useEffect(() => {
    if (!recipe) {
      setDisplayRecipe(null);
      recipeIdRef.current = null;
      return;
    }

    setIsFavorite(recipe.is_favorite ?? false);

    if (!recipe.id || recipeIdRef.current !== recipe.id) {
      setDisplayRecipe(recipe);
      setSelectedPersons(recipe.persons || 4);
      recipeIdRef.current = recipe.id ?? null;
    }
  }, [recipe]);

  const handleSaveAsPersonalRecipe = async () => {
    if (!displayRecipe || saving) return;

    setSaving(true);
    try {
      const recipeToSave = {
        title: displayRecipe.title,
        source: "personal",
        persons: displayRecipe.persons || selectedPersons,
        time_minutes: displayRecipe.time_minutes,
        oven_temperature: displayRecipe.oven_temperature ?? null,
        oven_mode: displayRecipe.oven_mode ?? null,
        category: displayRecipe.category || "other",
        ingredients: displayRecipe.ingredients || [],
        steps: displayRecipe.steps || [],
        tips: displayRecipe.tips || null,
        image: null, // AI recipes usually have null image
      };

      const response = await apiService.createRecipe(recipeToSave);

      onRecipeSaved?.(response.data);
      onClose();

    } catch (error) {
      console.error("Save recipe error:", error);
      Alert.alert("Error", "Could not save recipe. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const toggleFavorite = async () => {
    if (loading) return;
    
    setLoading(true);
  try {
    const response = await apiService.toggleFavorite(recipe.id);
      
      const updatedRecipe = response.data;
      setIsFavorite(updatedRecipe.is_favorite);

      // Notify parent component so list can update too
      onFavoriteChanged?.(updatedRecipe);

    } catch (error) {
      console.error("Toggle favorite error:", error);
      Alert.alert("Fout", "Kon favoriet status niet updaten");
    } finally {
      setLoading(false);
    }
  };

  const scaleRecipe = async (persons) => {
    if (persons === selectedPersons) return;

    if (persons === recipe.persons) {
      setDisplayRecipe(recipe);
      setSelectedPersons(persons);
      return;
    }

  try {
    setScaling(true);
    const response = await apiService.scaleRecipe(recipe.id, persons);

      setDisplayRecipe(response.data);
      setSelectedPersons(persons);

    } catch (err) {
      Alert.alert("Fout", "Kon recept niet aanpassen.");
    } finally {
      setScaling(false);
    }
  };

  const handleEdit = () => {
    if (recipe) {
      onEditPress?.(recipe);
    }
  };

  const openTimerForm = () => {
    setPendingDeleteTimerId(null);
    setTimerStepIndex(null);
    setTimerLabel("");
    setTimerMinutes("5");
    setTimerIcon(null);
    setTimerColor(DEFAULT_TIMER_COLOR);
    setShowTimerForm(true);
  };

  const closeTimerForm = () => {
    setShowTimerForm(false);
  };

  const selectTimerStep = (index) => {
    setTimerStepIndex(index);
  };

  const handleSaveTimer = async () => {
    const label = timerLabel.trim();
    const minutes = parseInt(timerMinutes, 10);

    if (timerStepIndex === null) {
      Alert.alert("Fout", "Kies een stap voor de timer.");
      return;
    }
    if (!label) {
      Alert.alert("Fout", "Geef de timer een naam.");
      return;
    }
    if (!Number.isFinite(minutes) || minutes <= 0) {
      Alert.alert("Fout", "Vul een geldig aantal minuten in.");
      return;
    }

    setSavingTimer(true);
    try {
      const response = await apiService.addTimer(recipe.id, {
        label,
        duration_seconds: minutes * 60,
        step_index: timerStepIndex,
        icon: timerIcon,
        color: timerColor,
      });
      setDisplayRecipe(response.data);
      setShowTimerForm(false);
    } catch (error) {
      console.error("Add timer error:", error);
      Alert.alert("Fout", "Kon timer niet opslaan.");
    } finally {
      setSavingTimer(false);
    }
  };

  const handleStartTimer = (timer) => {
    const started = startTimer({
      sourceId: timer.id,
      label: timer.label,
      durationSeconds: timer.duration_seconds,
      icon: timer.icon,
      color: timer.color,
    });
    if (!started) {
      Alert.alert("Timer", "Deze timer loopt al.");
    }
  };

  const handleDeleteTimer = async (timerId) => {
    setSavingTimer(true);
    try {
      const response = await apiService.deleteTimer(recipe.id, timerId);
      setDisplayRecipe(response.data);
      setPendingDeleteTimerId(null);
    } catch (error) {
      console.error("Delete timer error:", error);
      Alert.alert("Fout", "Kon timer niet verwijderen.");
    } finally {
      setSavingTimer(false);
    }
  };

  const toggleCookedToday = async () => {
    if (!displayRecipe?.id || markingCooked) return;

    const alreadyCooked = (displayRecipe.cooked_dates || []).includes(today);
    try {
      setMarkingCooked(true);
      const response = alreadyCooked
        ? await apiService.unmarkCooked(displayRecipe.id, today)
        : await apiService.markCooked(displayRecipe.id, today);
      const updated = response.data;
      setDisplayRecipe((prev) =>
        prev ? { ...prev, cooked_dates: updated.cooked_dates } : updated
      );
      onCookedChanged?.(updated);
    } catch (error) {
      console.error("Toggle cooked error:", error);
      Alert.alert("Fout", "Kon de kookstatus niet opslaan.");
    } finally {
      setMarkingCooked(false);
    }
  };

  if (!visible || !recipe) {
    return null;
  }

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={false}
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        {/* Header */}
        <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Ionicons name="close" size={28} color="#333" />
          </TouchableOpacity>

          <Text style={styles.title} numberOfLines={1}>
            {recipe.title}
          </Text>

           {/* Edit Button */}
            <TouchableOpacity 
              onPress={handleEdit}
              style={styles.headerButton}
            >
              <Entypo name="edit" size={24} color="#1e90ff" />
            </TouchableOpacity>

          {/* Save Button - Only for AI Recipes */}
          {recipe.source === "ai" && (
            <TouchableOpacity 
              onPress={handleSaveAsPersonalRecipe}
              disabled={saving}
              style={styles.saveButton}
            >
              <MaterialIcons 
                name="save" 
                size={26} 
                color={saving ? "#999" : "#16a34a"} 
              />
            </TouchableOpacity>
          )}

          {recipe.source !== "ai" && (
            <TouchableOpacity 
              onPress={toggleFavorite} 
              disabled={loading}
              style={styles.favoriteButton}
            >
              <Ionicons
                name={isFavorite ? "heart" : "heart-outline"}
                size={28}
                color={isFavorite ? "#e74c3c" : "#666"}
              />
            </TouchableOpacity>
          )}
        </View>

        <ScrollView
          ref={scrollViewRef}
          style={styles.scrollContainer}
          contentContainerStyle={{ paddingBottom: insets.bottom + 32 }}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
          automaticallyAdjustKeyboardInsets={true}
          keyboardDismissMode="interactive"
        >
          {/* Recipe Image */}
  {recipe.image && (
    <Image
      source={buildRecipeImageUrl(recipe.source, recipe.image)}
      style={styles.recipeImage}
      contentFit="cover"
      cachePolicy="memory-disk"
      transition={200}
    />
  )}

          {/* Meta Info */}
          <View style={styles.metaContainer}>
            <View style={styles.metaRow}>
              <View style={styles.scaleContainer}>
                <Ionicons name="people-outline" size={20} color="#555" />
                <Text style={styles.scaleTitle}>Personen</Text>

                <View style={styles.scaleButtons}>
                  {[2, 4].map((p) => (
                    <TouchableOpacity
                      key={p}
                      onPress={() => scaleRecipe(p)}
                      style={[
                        styles.personButton,
                        selectedPersons === p && styles.personButtonSelected,
                      ]}
                    >
                      <Text
                        style={[
                          styles.personText,
                          selectedPersons === p && styles.personTextSelected,
                        ]}
                      >
                        {p}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>

              {recipe.time_minutes && (
                <View style={styles.infoRow}>
                  <Ionicons name="time-outline" size={20} color="#555" />
                  <Text style={styles.infoText}>
                    {recipe.time_minutes} minuten
                  </Text>
                </View>
              )}
            </View>

            {((recipe.category && recipe.category !== "other") ||
              recipe.oven_temperature != null ||
              displayRecipe?.id) && (
              <View style={styles.metaRow}>
                {recipe.oven_temperature != null && (
                  <View style={[styles.infoRow, styles.ovenInfoRow]}>
                    <Image
                      source={getOvenModeIcon(recipe.oven_mode)}
                      style={styles.ovenIcon}
                    />
                    <Text style={[styles.infoText, styles.ovenInfoText]}>
                      {recipe.oven_temperature} °C
                    </Text>
                  </View>
                )}

                {recipe.category && recipe.category !== "other" && (
                  <View style={[styles.infoRow, styles.tagInfoRow]}>
                    <Ionicons name="pricetag-outline" size={20} color="#555" />
                    <Text style={styles.infoText}>{recipe.category}</Text>
                  </View>
                )}

                {displayRecipe?.id && (
                  <TouchableOpacity
                    style={[
                      styles.todayStamp,
                      isCookedToday && styles.todayStampActive,
                    ]}
                    onPress={toggleCookedToday}
                    activeOpacity={0.8}
                    disabled={markingCooked}
                  >
                    <Text
                      style={[
                        styles.todayStampText,
                        isCookedToday && styles.todayStampTextActive,
                      ]}
                    >
                      {isCookedToday ? "TODAY ✓" : "TODAY"}
                    </Text>
                  </TouchableOpacity>
                )}
              </View>
            )}
          </View>

          {/* Ingredients */}
          <Text style={styles.sectionTitle}>Ingrediënten</Text>
          <View style={styles.ingredientsContainer}>
            {displayRecipe?.ingredients?.map((item, index) => (
              <View key={index} style={styles.ingredientRow}>
                <Text style={styles.quantity}>{item.quantity || ""}</Text>
                <Text style={styles.ingredientName}>{item.name}</Text>
              </View>
            ))}
          </View>

          {/* Steps */}
          <Text style={styles.sectionTitle}>Bereiding</Text>
          {recipe.steps?.map((step, index) => {
            const stepTimers = (displayRecipe?.timers || []).filter(
              (timer) => timer.step_index === index
            );

            return (
              <View key={index} style={styles.stepContainer}>
                <Text style={styles.stepNumber}>{index + 1}</Text>
                <View style={styles.stepContent}>
                  <Text style={styles.stepText}>{step}</Text>

                  {stepTimers.length > 0 && (
                    <View style={styles.stepTimersRow}>
                      {stepTimers.map((timer) => {
                        return (
                        <View key={timer.id} style={styles.timerChipGroup}>
                          <TouchableOpacity
                            style={[
                              styles.timerChip,
                              {
                                backgroundColor: TIMER_CHIP_COLOR.background,
                                borderColor: TIMER_CHIP_COLOR.border,
                              },
                            ]}
                            activeOpacity={0.8}
                            onLongPress={() =>
                              setPendingDeleteTimerId(timer.id)
                            }
                            onPress={() => {
                              if (pendingDeleteTimerId === timer.id) {
                                setPendingDeleteTimerId(null);
                                return;
                              }
                              handleStartTimer(timer);
                            }}
                          >
                            <Ionicons
                              name="timer-outline"
                              size={16}
                              color={TIMER_CHIP_COLOR.text}
                            />
                            <Text
                              style={[
                                styles.timerChipLabel,
                                { color: TIMER_CHIP_COLOR.text },
                              ]}
                            >
                              {timer.label}
                            </Text>
                          </TouchableOpacity>

                          {pendingDeleteTimerId === timer.id && (
                            <TouchableOpacity
                              style={styles.timerDeleteChip}
                              onPress={() => handleDeleteTimer(timer.id)}
                              disabled={savingTimer}
                            >
                              <Ionicons
                                name="trash-outline"
                                size={16}
                                color="#fff"
                              />
                              <Text
                                style={styles.timerDeleteChipText}
                                numberOfLines={1}
                              >
                                Verwijderen
                              </Text>
                            </TouchableOpacity>
                          )}
                        </View>
                        );
                      })}
                    </View>
                  )}
                </View>
              </View>
            );
          })}

          {showTimerForm ? (
            <View
              style={styles.timerForm}
              onLayout={(e) => {
                timerFormY.current = e.nativeEvent.layout.y;
              }}
            >
              <Text style={styles.timerFormLabel}>Kies een stap</Text>
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                style={styles.stepChips}
              >
                {displayRecipe?.steps?.map((step, index) => (
                  <TouchableOpacity
                    key={index}
                    style={[
                      styles.stepChip,
                      timerStepIndex === index && styles.stepChipSelected,
                    ]}
                    onPress={() => selectTimerStep(index)}
                  >
                    <Text
                      style={[
                        styles.stepChipText,
                        timerStepIndex === index && styles.stepChipTextSelected,
                      ]}
                    >
                      Stap {index + 1}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>

              <Text style={styles.timerFormLabel}>Naam</Text>
              <TextInput
                style={styles.timerInput}
                value={timerLabel}
                onChangeText={setTimerLabel}
                onFocus={scrollToTimerForm}
                placeholder="bijv. koken"
                placeholderTextColor="#999"
              />

              <Text style={styles.timerFormLabel}>Minuten</Text>
              <TextInput
                style={styles.timerInput}
                value={timerMinutes}
                onChangeText={setTimerMinutes}
                onFocus={scrollToTimerForm}
                keyboardType="number-pad"
                placeholder="5"
                placeholderTextColor="#999"
              />

              <Text style={styles.timerFormLabel}>Icoon</Text>
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                style={styles.iconPicker}
              >
                <TouchableOpacity
                  style={[
                    styles.iconOption,
                    timerIcon === null && styles.iconOptionSelected,
                  ]}
                  onPress={() => setTimerIcon(null)}
                >
                  <Ionicons name="timer-outline" size={24} color="#e74c3c" />
                </TouchableOpacity>
                {TIMER_ICON_KEYS.map((key) => (
                  <TouchableOpacity
                    key={key}
                    style={[
                      styles.iconOption,
                      timerIcon === key && styles.iconOptionSelected,
                    ]}
                    onPress={() => setTimerIcon(key)}
                  >
                    <Image
                      source={TIMER_ICONS[key]}
                      style={styles.iconOptionImage}
                      contentFit="contain"
                    />
                  </TouchableOpacity>
                ))}
              </ScrollView>

              <Text style={styles.timerFormLabel}>Kleur</Text>
              <View style={styles.colorPicker}>
                {TIMER_COLORS.map((option) => {
                  const selected = timerColor === option.value;

                  return (
                    <TouchableOpacity
                      key={option.value}
                      style={[
                        styles.colorOption,
                        { backgroundColor: option.value },
                        selected && styles.colorOptionSelected,
                      ]}
                      onPress={() => setTimerColor(option.value)}
                      accessibilityLabel={option.label}
                    >
                      {selected && (
                        <Ionicons name="checkmark" size={18} color="#fff" />
                      )}
                    </TouchableOpacity>
                  );
                })}
              </View>

              <View style={styles.timerFormButtons}>
                <TouchableOpacity
                  style={[styles.timerButton, styles.timerCancelButton]}
                  onPress={closeTimerForm}
                  disabled={savingTimer}
                >
                  <Text style={styles.timerCancelText}>Annuleren</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.timerButton, styles.timerSaveButton]}
                  onPress={handleSaveTimer}
                  disabled={savingTimer}
                >
                  <Text style={styles.timerSaveText}>
                    {savingTimer ? "Opslaan..." : "Opslaan"}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          ) : (
            <TouchableOpacity
              style={styles.addTimerButton}
              onPress={openTimerForm}
            >
              <Ionicons name="add" size={20} color="#e74c3c" />
              <Text style={styles.addTimerText}>Timer toevoegen</Text>
            </TouchableOpacity>
          )}

          {/* Tips */}
          {recipe.tips && recipe.tips.length > 0 && (
            <>
              <Text style={styles.sectionTitle}>Tips</Text>
              <View style={styles.tipsContainer}>
                <Text style={styles.tipsText}>{recipe.tips}</Text>
              </View>
            </>
          )}
        </ScrollView>
      </View>

      <TimerOverlay />
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fafafa",
  },

  header: {
    backgroundColor: "#fff",
    paddingBottom: 15,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
    flexDirection: "row",
    alignItems: "center",
  },

  closeButton: {
    marginRight: 15,
  },

  title: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#1a1a1a",
    flex: 1,
  },

  favoriteButton: {
    padding: 8,
  },

  scrollContainer: {
    flex: 1,
  },

  recipeImage: {
    width: "100%",
    height: 260,
    backgroundColor: "#eee",
  },

  metaContainer: {
    padding: 20,
    gap: 12,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },

  metaRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    alignItems: "center",
    gap: 12,
  },

  scaleContainer: {
    alignItems: "center",
    flexDirection: "row",
  },

  scaleTitle: {
    color: "#333",
    fontSize: 16,
    marginLeft: 8,
  },

  scaleButtons: {
    flexDirection: "row",
  },

  personButton: {
    width: 28,
    height: 28,
    borderRadius: 2,
    borderWidth: 1,
    borderColor: "#ddd",
    justifyContent: "center",
    alignItems: "center",
    marginHorizontal: 4,
  },

  personButtonSelected: {
    backgroundColor: "#e74c3c",
    borderColor: "#e74c3c",
  },

  personText: {
    fontWeight: "bold",
    color: "#333",
    fontSize: 16,
  },

  personTextSelected: {
    color: "white",
  },

  infoRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fafafa",
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
  },

  infoText: {
    marginLeft: 8,
    fontSize: 16,
    color: "#333",
  },

  tagInfoRow: {
    backgroundColor: "transparent",
    paddingHorizontal: 0,
    paddingVertical: 4,
  },

  ovenIcon: {
    width: 18,
    height: 18,
    tintColor: "#e74c3c",
  },

  ovenInfoRow: {
    backgroundColor: "transparent",
    paddingHorizontal: 0,
    paddingVertical: 4,
  },

  ovenInfoText: {
    fontSize: 16,
    marginLeft: 6,
    color: "#e74c3c",
    fontWeight: "700",
  },

  todayStamp: {
    flexDirection: "row",
    alignItems: "center",
    marginLeft: 12,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderWidth: 2,
    borderColor: "#16a34a",
    borderRadius: 8,
    transform: [{ rotate: "-4deg" }],
  },

  todayStampActive: {
    backgroundColor: "#16a34a",
  },

  todayStampText: {
    fontSize: 15,
    fontWeight: "800",
    letterSpacing: 2,
    color: "#16a34a",
  },

  todayStampTextActive: {
    color: "#fff",
  },

  sectionTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#1a1a1a",
    marginTop: 25,
    marginBottom: 12,
    paddingHorizontal: 20,
  },

  ingredientsContainer: {
    backgroundColor: "#fff",
    paddingHorizontal: 20,
    paddingVertical: 15,
  },

  ingredientRow: {
    flexDirection: "row",
    paddingVertical: 9,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },

  quantity: {
    width: 90,
    fontWeight: "600",
    color: "#e74c3c",
  },

  ingredientName: {
    flex: 1,
    color: "#333",
    fontSize: 16,
  },

  stepContainer: {
    flexDirection: "row",
    marginBottom: 20,
    backgroundColor: "#fff",
    padding: 18,
    borderRadius: 12,
    marginHorizontal: 20,
  },

  stepNumber: {
    fontWeight: "bold",
    fontSize: 18,
    color: "#e74c3c",
    marginRight: 14,
    width: 26,
  },

  stepContent: {
    flex: 1,
  },

  stepText: {
    fontSize: 16,
    lineHeight: 24,
    color: "#333",
  },

  stepTimersRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 12,
  },

  timerChip: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    backgroundColor: "#fee2e2",
    borderWidth: 1,
    borderColor: "#fca5a5",
  },

  timerChipLabel: {
    marginLeft: 6,
    fontSize: 14,
    fontWeight: "500",
    color: "#be123c",
  },

  timerChipGroup: {
    position: "relative",
  },

  timerDeleteChip: {
    position: "absolute",
    bottom: 38,
    left: 0,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    width: 128,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    backgroundColor: "#e74c3c",
    zIndex: 20,
    elevation: 6,
  },

  timerDeleteChipText: {
    marginLeft: 6,
    fontSize: 14,
    fontWeight: "600",
    color: "#fff",
  },

  tipsContainer: {
    backgroundColor: "#fff3cd",
    marginHorizontal: 20,
    padding: 18,
    borderRadius: 12,
    borderLeftWidth: 5,
    borderLeftColor: "#f4c430",
    marginBottom: 30,
  },

  tipsText: {
    fontSize: 16,
    lineHeight: 24,
    color: "#444",
  },

  saveButton: {
    padding: 8,
    marginLeft: 8,
  },

  addTimerButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 12,
    marginTop: 8,
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#e74c3c",
    borderStyle: "dashed",
  },

  addTimerText: {
    marginLeft: 6,
    color: "#e74c3c",
    fontWeight: "600",
    fontSize: 16,
  },

  timerForm: {
    backgroundColor: "#fff",
    marginHorizontal: 20,
    marginTop: 8,
    marginBottom: 20,
    borderRadius: 12,
    padding: 16,
  },

  timerFormLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: "#666",
    marginTop: 12,
    marginBottom: 6,
  },

  stepChips: {
    flexDirection: "row",
  },

  stepChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 16,
    backgroundColor: "#f0f0f0",
    marginRight: 8,
  },

  stepChipSelected: {
    backgroundColor: "#e74c3c",
  },

  stepChipText: {
    color: "#555",
    fontSize: 14,
  },

  stepChipTextSelected: {
    color: "#fff",
  },

  timerInput: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 16,
    color: "#333",
    backgroundColor: "#fafafa",
  },

  iconPicker: {
    flexDirection: "row",
  },

  iconOption: {
    width: 48,
    height: 48,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#fafafa",
    borderWidth: 2,
    borderColor: "#eee",
    marginRight: 8,
  },

  iconOptionSelected: {
    borderColor: "#e74c3c",
    backgroundColor: "#fee2e2",
  },

  iconOptionImage: {
    width: 24,
    height: 24,
  },

  colorPicker: {
    flexDirection: "row",
    gap: 10,
  },

  colorOption: {
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 2,
    borderColor: "transparent",
  },

  colorOptionSelected: {
    borderColor: "#282c34",
  },

  timerFormButtons: {
    flexDirection: "row",
    justifyContent: "flex-end",
    marginTop: 16,
  },

  timerButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 10,
    marginLeft: 10,
  },

  timerCancelButton: {
    backgroundColor: "#f0f0f0",
  },

  timerCancelText: {
    color: "#555",
    fontWeight: "600",
  },

  timerSaveButton: {
    backgroundColor: "#e74c3c",
  },

  timerSaveText: {
    color: "#fff",
    fontWeight: "600",
  },
});

export default RecipeModal;