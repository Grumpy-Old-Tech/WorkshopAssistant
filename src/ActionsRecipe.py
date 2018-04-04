#!/usr/bin/env python

import json
import urllib.request
from ActionsPushbullet import pushmessage

def getrecipe(phase):
    ingrequest = phase
    ingredientsidx=ingrequest.find('for')
    ingrequest=ingrequest[ingredientsidx:]
    ingrequest=ingrequest.replace('for',"",1)
    ingrequest=ingrequest.replace("'}","",1)
    ingrequest=ingrequest.strip()
    ingrequest=ingrequest.replace(" ","%20",1)
    appid='ENTER-YOUR-APPID-HERE'
    appkey='ENTER-YOUR-APP-KEY-HERE'
    recipeurl = 'https://api.edamam.com/search?q='+ingrequest+'&app_id='+appid+'&app_key='+appkey
    print(recipeurl)
    recipedetails = urllib.request.urlopen(recipeurl)
    recipedetails=recipedetails.read()
    recipedetails = recipedetails.decode('utf-8')
    recipedetails=json.loads(recipedetails)
    recipe_ingredients=str(recipedetails['hits'][0]['recipe']['ingredientLines'])
    recipe_url=recipedetails['hits'][0]['recipe']['url']
    recipe_name=recipedetails['hits'][0]['recipe']['label']
    recipe_ingredients=recipe_ingredients.replace('[','',1)
    recipe_ingredients=recipe_ingredients.replace(']','',1)
    recipe_ingredients=recipe_ingredients.replace('"','',1)
    recipe_ingredients=recipe_ingredients.strip()
    print(recipe_name)
    print("")
    print(recipe_url)
    print("")
    print(recipe_ingredients)
    compiled_recipe_info="\nRecipe Source URL:\n"+recipe_url+"\n\nRecipe Ingredients:\n"+recipe_ingredients
    pushmessage(str(recipe_name),str(compiled_recipe_info))

