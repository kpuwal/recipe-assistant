// __tests__/RecipeModal.test.js                                                                                                                                                                                                                       
    // Minimal test suite for RecipeModal component                                                                                                                                                                                                        
                                                                                                                                                                                                                                                           
    import React from "react";                                                                                                                                                                                                                             
    import { render } from "@testing-library/react-native";                                                                                                                                                                                                
    import RecipeModal from "../RecipeModal";                                                                                                                                                                                                              
                                                                                                                                                                                                                                                           
    describe("RecipeModal", () => {                                                                                                                                                                                                                        
      const sampleRecipe = {                                                                                                                                                                                                                               
        title: "Spaghetti Bolognese",                                                                                                                                                                                                                      
        persons: 4,                                                                                                                                                                                                                                        
        time_minutes: 45,
        category: "pasta",
        ingredients: [
          { name: "Spaghetti", quantity: "400g" },
          { name: "Ground beef", quantity: "250g" },
          { name: "Tomato sauce", quantity: "200ml" },
        ],
        steps: [
          "Boil the spaghetti according to package instructions.",
          "Brown the ground beef in a pan.",
          "Add tomato sauce to the beef and simmer.",
          "Combine spaghetti with sauce and serve.",
        ],
        tips: "Add a pinch of sugar to balance acidity.",
        image: "",
      };
  
      it("renders the recipe title", () => {
        const { getByText } = render(
          <RecipeModal visible={true} onClose={jest.fn()} recipe={sampleRecipe} />
        );
        expect(getByText("Spaghetti Bolognese")).toBeTruthy();
      });
  
      it("displays all ingredients", () => {
        const { getByText } = render(
          <RecipeModal visible={true} onClose={jest.fn()} recipe={sampleRecipe} />
        );
  
        sampleRecipe.ingredients.forEach((ing) => {
          // Expect each ingredient line to appear (quantity + name)
          expect(getByText(`${ing.quantity} ${ing.name}`)).toBeTruthy();
        });
      });
  
      it("shows all preparation steps", () => {
        const { getByText } = render(
          <RecipeModal visible={true} onClose={jest.fn()} recipe={sampleRecipe} />
        );
  
        sampleRecipe.steps.forEach((step, idx) => {
          // Steps are usually rendered with an index prefix like "Step 1"
          expect(getByText(step)).toBeTruthy();
        });
      });
    });
