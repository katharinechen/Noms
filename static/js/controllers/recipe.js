'use strict';

// controls the display of a single recipe
app.controller('Recipe', ['$scope', '$http', '$location', function($scope, $http, $location) {
    var urlKey = $scope.preload.urlKey;

    $http({method: 'GET', url: '/api/recipe/' + urlKey}).then(function(recipe) {
        $scope.recipe = recipe.data;
    });

    $scope.abc = {
      name: 'awesome user'
    }; 
}]);

