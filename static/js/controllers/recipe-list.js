'use strict';

app.controller('RecipeListCtrl', ['$scope', 'recipeFactory', function($scope, recipeFactory) {
    // Initialize Variables
    $scope.recipes;
    $scope.status;

    // Read all recipes
    $scope.showList = function() {
        recipeFactory.listRecipes().then(function(response) {
            $scope.recipes = response.data;
        }), function (error) {
            $scope.status = "Unable to load customer data: " + error.message;
        };
    };
}]);