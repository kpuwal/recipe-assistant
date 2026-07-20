# backend/tests/test_recipe.py                                                                                                                                                                                                                         
import json                                                                                                                                                                                                                                            
from fastapi.testclient import TestClient                                                                                                                                                                                                              
from main import app  # FastAPI instance defined in backend/main.py                                                                                                                                                                                    
                                                                                                                                                                                                                                                        
client = TestClient(app)                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                        
# ----------------------------------------------------------------------                                                                                                                                                                               
# Helper – a minimal recipe payload used by several tests                                                                                                                                                                                              
# ----------------------------------------------------------------------                                                                                                                                                                               
def sample_recipe():                                                                                                                                                                                                                                   
    return {                                                                                                                                                                                                                                           
        "title": "Test Pancakes",                                                                                                                                                                                                                      
        "source": "personal",                                                                                                                                                                                                                          
        "persons": 2,                                                                                                                                                                                                                                  
        "time_minutes": 15,                                                                                                                                                                                                                            
        "category": "breakfast",                                                                                                                                                                                                                       
        "ingredients": [                                                                                                                                                                                                                               
            {"name": "Flour", "quantity": "200g"},                                                                                                                                                                                                     
            {"name": "Eggs", "quantity": "2"},                                                                                                                                                                                                         
        ],                                                                                                                                                                                                                                             
        "steps": ["Mix ingredients", "Cook on skillet"],                                                                                                                                                                                               
        "tips": "Serve with syrup",                                                                                                                                                                                                                    
        "image": ""                                                                                                                                                                                                                                    
    }                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                        
# ----------------------------------------------------------------------                                                                                                                                                                               
# 1️⃣ Create a recipe and retrieve it back                                                                                                                                                                                                              
# ----------------------------------------------------------------------                                                                                                                                                                               
def test_create_and_get_recipe():                                                                                                                                                                                                                      
    # ---- CREATE ----                                                                                                                                                                                                                                 
    create_resp = client.post("/recipes", json=sample_recipe())                                                                                                                                                                                        
    assert create_resp.status_code == 200                                                                                                                                                                                                              
    created = create_resp.json()                                                                                                                                                                                                                       
    assert "id" in created  # repository assigns an ID                                                                                                                                                                                                 
    recipe_id = created["id"]                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                        
    # ---- GET ----                                                                                                                                                                                                                                    
    get_resp = client.get(f"/recipes/{recipe_id}")                                                                                                                                                                                                     
    assert get_resp.status_code == 200                                                                                                                                                                                                                 
    fetched = get_resp.json()                                                                                                                                                                                                                          
    assert fetched["title"] == "Test Pancakes"                                                                                                                                                                                                         
    assert fetched["persons"] == 2                                                                                                                                                                                                                     
    # The default `is_favorite` flag should be False                                                                                                                                                                                                   
    assert fetched.get("is_favorite") is False                                                                                                                                                                                                         
                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                        
# ----------------------------------------------------------------------                                                                                                                                                                               
# 2️⃣ Toggle the favorite flag and verify the field name                                                                                                                                                                                                
# ----------------------------------------------------------------------                                                                                                                                                                               
def test_update_favorite_flag():                                                                                                                                                                                                                       
    # Create a fresh recipe                                                                                                                                                                                                                            
    create_resp = client.post("/recipes", json=sample_recipe())                                                                                                                                                                                        
    recipe_id = create_resp.json()["id"]                                                                                                                                                                                                               
                                                                                                                                                                                                                                                        
    # ---- TOGGLE FAVORITE ----                                                                                                                                                                                                                        
    fav_resp = client.put(f"/recipes/{recipe_id}/favorite")
    assert fav_resp.status_code == 200
    fav_data = fav_resp.json()

    # The endpoint returns the whole Recipe model; the flag name is `is_favorite`
    assert "is_favorite" in fav_data
    assert fav_data["is_favorite"] is True  # first toggle should set it to True

    # Toggle again – should become False
    fav_resp2 = client.put(f"/recipes/{recipe_id}/favorite")
    assert fav_resp2.status_code == 200
    assert fav_resp2.json()["is_favorite"] is False


# ----------------------------------------------------------------------
# 3 Delete a recipe and ensure it is gone
# ----------------------------------------------------------------------
def test_delete_recipe():
    # Create a recipe
    recipe_id = client.post("/recipes", json=sample_recipe()).json()["id"]

    # ---- DELETE ----
    del_resp = client.delete(f"/recipes/{recipe_id}")
    assert del_resp.status_code == 200
    assert del_resp.json().get("success") is True

    # Verify it no longer exists
    get_resp = client.get(f"/recipes/{recipe_id}")
    assert get_resp.status_code == 200
    # The endpoint returns an error dict when a recipe is missing
    assert get_resp.json().get("error") == "Recipe not found"
