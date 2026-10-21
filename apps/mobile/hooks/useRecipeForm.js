import React, { useState, useEffect, useCallback } from "react";
import { Alert } from "react-native";

const INITIAL_FORM = {
  title: "",
  persons: "",
  time_minutes: "",
  oven_temperature: "",
  oven_mode: null,
  category: "other",
  ingredients: [{ name: "", quantity: "" }],
  steps: [""],
  tips: "",
  image: "",
};

const useRecipeForm = ({ onSubmit, onSuccess, initialValues = null }) => {
  const [form, setForm] = useState(INITIAL_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [imageAsset, setImageAsset] = useState(null);
  const [imageRemoved, setImageRemoved] = useState(false);

  useEffect(() => {
    setImageAsset(null);
    setImageRemoved(false);

    if (initialValues) {
      setForm({
        title: initialValues.title || "",
        persons: initialValues.persons ? String(initialValues.persons) : "",
        time_minutes: initialValues.time_minutes
          ? String(initialValues.time_minutes)
          : "",
        oven_temperature: initialValues.oven_temperature
          ? String(initialValues.oven_temperature)
          : "",
        oven_mode: initialValues.oven_mode || null,
        category: initialValues.category || "other",
        ingredients: initialValues.ingredients?.length
          ? initialValues.ingredients
          : [{ name: "", quantity: "" }],
        steps: initialValues.steps?.length ? initialValues.steps : [""],
        tips: initialValues.tips || "",
        image: initialValues.image || "",
      });
    } else {
      setForm(INITIAL_FORM);
    }
  }, [initialValues]);

  const updateField = useCallback((field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
  }, []);

  const selectImage = useCallback(asset => {
    setImageAsset(asset);
    setImageRemoved(false);
  }, []);

  const removeImage = useCallback(() => {
    setImageAsset(null);
    setImageRemoved(true);
  }, []);

  const updateIngredient = useCallback((index, field, value) => {
    setForm(prev => {
      const newIngredients = [...prev.ingredients];
      newIngredients[index] = { ...newIngredients[index], [field]: value };
      return { ...prev, ingredients: newIngredients };
    });
  }, []);

  const addIngredient = useCallback(() => {
    setForm(prev => ({
      ...prev,
      ingredients: [...prev.ingredients, { name: "", quantity: "" }],
    }));
  }, []);

  const removeIngredient = useCallback(index => {
    setForm(prev => {
      if (prev.ingredients.length === 1) return prev;
      return {
        ...prev,
        ingredients: prev.ingredients.filter((_, i) => i !== index),
      };
    });
  }, []);

  const addStep = useCallback(() => {
    setForm(prev => ({ ...prev, steps: [...prev.steps, ""] }));
  }, []);

  const removeStep = useCallback(index => {
    setForm(prev => {
      if (prev.steps.length === 1) return prev;
      return { ...prev, steps: prev.steps.filter((_, i) => i !== index) };
    });
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!form.title.trim()) {
      Alert.alert("Fout", "Recipe title is required");
      return;
    }

    const validIngredients = form.ingredients.filter(ing => ing.name.trim());
    if (validIngredients.length === 0) {
      Alert.alert(
        "Fout",
        "Voeg ten minste één ingrediënt met een naam toe"
      );
      return;
    }

    const validSteps = form.steps.filter(s => s.trim());
    if (validSteps.length === 0) {
      Alert.alert("Fout", "Voeg ten minste één bereidingsstap toe");
      return;
    }

    const recipeData = {
      title: form.title.trim(),
      source: "personal",
      persons: form.persons ? parseInt(form.persons) : null,
      time_minutes: form.time_minutes ? parseInt(form.time_minutes) : null,
      oven_temperature: form.oven_temperature
        ? parseInt(form.oven_temperature)
        : null,
      oven_mode: form.oven_mode || null,
      category: form.category.trim() || "other",
      ingredients: validIngredients,
      steps: validSteps,
      tips: form.tips.trim() || null,
      image: imageRemoved ? null : form.image.trim() || null,
    };

    setSubmitting(true);
    try {
      const response = await onSubmit(recipeData, {
        imageAsset,
        imageRemoved,
      });
      onSuccess?.(response.data);
      setForm(INITIAL_FORM);
      setImageAsset(null);
      setImageRemoved(false);
    } catch (error) {
      console.error(error);
      Alert.alert("Fout", "Kon recept niet opslaan. Probeer het opnieuw.");
    } finally {
      setSubmitting(false);
    }
  }, [form, imageAsset, imageRemoved, onSubmit, onSuccess]);

  return {
    form,
    submitting,
    imageAsset,
    imageRemoved,
    handleSubmit,
    updateField,
    updateIngredient,
    addIngredient,
    removeIngredient,
    addStep,
    removeStep,
    selectImage,
    removeImage,
  };
};

export default useRecipeForm;
