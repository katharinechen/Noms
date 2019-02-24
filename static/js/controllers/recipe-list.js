'use strict';

app.controller('RecipeListCtrl', ['$scope', 'recipeFactory', function($scope, recipeFactory) {
    // Initialize Variables
    $scope.recipes = [];
    $scope.status = null;

    // Read all recipes
    $scope.showList = function() {
        recipeFactory.listRecipes().then(
            (response) => {
                $scope.recipes = response.data;
            },
            (err) => {
                $scope.status = "Unable to load the recipe list";
            }
        );
    };
    $scope.showList();
}]);