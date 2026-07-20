   // __tests__/AddRecipeModal.test.js                                                                                                                                                                                                                    
    // Minimal test suite for AddRecipeModal component                                                                                                                                                                                                     
                                                                                                                                                                                                                                                           
    import React from "react";                                                                                                                                                                                                                             
    import { render, fireEvent, waitFor } from "@testing-library/react-native";                                                                                                                                                                            
    import AddRecipeModal from "../AddRecipeModal";                                                                                                                                                                                                        
    import axios from "axios";                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                           
    jest.mock("axios");                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                           
    describe("AddRecipeModal", () => {                                                                                                                                                                                                                     
      const mockOnClose = jest.fn();                                                                                                                                                                                                                       
      const mockOnRecipeAdded = jest.fn();                                                                                                                                                                                                                 
      const apiUrl = "http://localhost:3000";                                                                                                                                                                                                              
                                                                                                                                                                                                                                                           
      beforeEach(() => {                                                                                                                                                                                                                                   
        jest.clearAllMocks();                                                                                                                                                                                                                              
      });                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                           
      it("renders title input and updates value", () => {
        const { getByPlaceholderText } = render(
          <AddRecipeModal
            visible={true}
            onClose={mockOnClose}
            api_url={apiUrl}
            onRecipeAdded={mockOnRecipeAdded}
          />
        );
  
        const titleInput = getByPlaceholderText("Recipe Title *");
        fireEvent.changeText(titleInput, "Test Recipe");
        expect(titleInput.props.value).toBe("Test Recipe");
      });
  
      it("submits recipe and calls callbacks on success", async () => {
        const responseData = { id: 1, title: "Test Recipe" };
        axios.post.mockResolvedValueOnce({ data: responseData });
  
        const { getByPlaceholderText, getByText } = render(
          <AddRecipeModal
            visible={true}
            onClose={mockOnClose}
            api_url={apiUrl}
            onRecipeAdded={mockOnRecipeAdded}
          />
        );
  
        fireEvent.changeText(
          getByPlaceholderText("Recipe Title *"),
          "Test Recipe"
        );
        fireEvent.press(getByText("Save Recipe"));
  
        await waitFor(() => expect(axios.post).toHaveBeenCalledTimes(1));
        expect(axios.post).toHaveBeenCalledWith(
          `${apiUrl}/recipes`,
          expect.objectContaining({ title: "Test Recipe" })
        );
        expect(mockOnRecipeAdded).toHaveBeenCalledWith(responseData);
        expect(mockOnClose).toHaveBeenCalled();
      });
    });
