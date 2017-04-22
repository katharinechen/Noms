'use strict';

// controls the display of a single recipe
app.controller('Recipe', ['$scope', '$http', '$location', function($scope, $http, $location) {
    var urlKey = $scope.preload.urlKey;

    $http({method: 'GET', url: '/api/recipe/' + urlKey}).then(function(recipe) {
        $scope.recipe = recipe.data;
    });


    $scope.saveRecipe = function() {
    	return $http.post('/api/recipe/' + urlKey + '/save').then(
    		function successCallback() {
    			console.log("I am a success!!!"); 
    		}, function errorCallback() {
    			console.log("I am sad"); 
    		}
    	)
    }
}]);

