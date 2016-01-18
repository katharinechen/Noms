'use strict'; 

// controls the list of recipes
app.controller('RecipeList', ['$scope', '$http', function($scope, $http) {
    $http({method: 'GET', url: '/api/recipe/list'}).then(function(recipelist) {
        $scope.recipes = recipelist.data; 
    }); 
}]); 