'use strict';

// root angular app
var app = angular.module('noms', ['ngMaterial', 'ngMessages']);

app.controller("Preload", ['$rootScope', '$window', function ($rootScope, $window) {
    // the nomsPreload object on the window is used by jinja templates to pass
    // server-side data to the angular app
    if ($window.nomsPreload) {
        $rootScope.preload = JSON.parse($window.nomsPreload);
    }
}]);

app.factory('recipeFactory', ['$http', function($http) {
    var recipeFactory = {};

    // Create a new recipe
    recipeFactory.create = function(recipe) {
        return $http.post('/api/recipe/create', recipe);
    };

    // Read a single recipe
    recipeFactory.read = function(urlKey) {
        return $http.get('/api/recipe/' + urlKey);
    };

    // Delete a single recipe
    recipeFactory.delete = function(urlKey) {
        return $http.post('/api/recipe/' + urlKey + '/delete');
    };

    recipeFactory.update = function(recipe, urlKey) {
        return $http.post('/api/recipe/' + urlKey + '/save', recipe);
    };

    // Read all recipes
    recipeFactory.listRecipes = function() {
        return $http.get('api/recipe/list');
    };

    return recipeFactory;
}]);