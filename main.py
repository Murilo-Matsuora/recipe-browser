import requests
from flask import Flask, render_template, url_for, redirect, request

api_url = "https://www.themealdb.com/api/json/v1/1"
FILTER_MAP = {
    'c': ["Categories", "Category"],
    'a': ["Regions", "Region"],
    'i': ["Main Ingredients", "Main Ingredient"]
}

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/filter/<filter_type>", methods=['GET'])
def filter_list(filter_type):
    filter_type_full = FILTER_MAP.get(filter_type)[0]
    if not filter_type_full:
        return redirect(url_for('home'))
    
    params = {
        f"{filter_type}": "list"
    }
    response = requests.get(f"{api_url}/list.php", params=params)
    data = response.json()
    # print(data)
    filtered_elements = data.get("meals", [])

    return render_template("filter-list.html", elements=filtered_elements, filter_type=filter_type, filter_type_full=filter_type_full)

@app.route("/filter/<filter_type>/<value>", methods=['GET'])
def filter_results(filter_type, value):
    filter_type_full = FILTER_MAP.get(filter_type)[1]
    if not filter_type_full:
        return redirect(url_for('home'))
    
    params = {
        f"{filter_type}": value
    }
    response = requests.get(f"{api_url}/filter.php", params=params)
    data = response.json()
    meals = data.get("meals", [])
    # print(meals)

    return render_template("filter-results.html", meals=meals, filter_type=filter_type, filter_type_full=filter_type_full, value=value)

@app.route("/recipe/<id>", methods=['GET'])
def show_recipe(id):
    response = requests.get(f"{api_url}/lookup.php?i={id}")
    data = response.json()
    meal = data.get("meals", [])[0]

    ingredients = []
    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")
        
        if ingredient and ingredient.strip():
            ingredients.append({
                "item": ingredient,
                "measure": measure if measure else ""
            })

    instructions = meal.get("strInstructions", "").split("\r\n")
    instructions = [step for step in instructions if step.strip()]
    instructions = [step for step in instructions if (step[:4] not in "STEP")]
    
    youtube_id = None
    if meal.get("strYoutube"):
        youtube_id = meal.get("strYoutube").split("v=")[-1]

    filter_type = request.args.get('filter_type')
    filter_value = request.args.get('value')
    
    filter_map = {'c': 'Categories', 'a': 'Regions', 'i': 'Ingredients'}
    filter_type_full = filter_map.get(filter_type)

    return render_template(
        "recipe.html", 
        meal=meal, 
        ingredients=ingredients, 
        instructions=instructions,
        youtube_id=youtube_id,
        filter_type=filter_type,
        filter_value=filter_value,
        filter_type_full=filter_type_full
    )

@app.route("/random")
def random_recipe():
    response = requests.get(f"{api_url}/random.php")
    data = response.json()
    meal = data.get("meals", [])

    if meal:
        random_id = meal[0]['idMeal']
        return redirect(url_for('show_recipe', id=random_id))
    
    return redirect(url_for('home'))

@app.route("/search")
def search():
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('home'))

    params = {'s': query}
    response = requests.get(f"{api_url}/search.php", params=params)
    data = response.json()
    
    meals = data.get("meals")
    if meals is None:
        meals = []

    return render_template(
        "filter-results.html", 
        meals=meals, 
        filter_type_full="Search Results", 
        value=query,
        filter_type="search"
    )

if __name__ == "__main__":
    app.run(debug=True)