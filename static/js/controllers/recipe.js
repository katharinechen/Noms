'use strict';

// controls the display of a single recipe
app.controller('Recipe', ['$scope', '$http', '$location', function($scope, $http, $location) {
    var urlKey = $scope.preload.urlKey;

    $http({method: 'GET', url: '/api/recipe/' + urlKey}).then(function(recipe) {
        $scope.recipe = $scope.buildRecipeObjects(recipe.data); 
    });

    // create a recipe object that is easy for the front-end to use
    $scope.buildRecipeObjects = function(data) { 
        var recipe = {}; 
        // set all attributes 
        for (var key in data) { 
            recipe[key] = data[key]; 
        } 
        // reset the following 
        $scope.restructureArray(recipe, 'ingredients'); 
        $scope.restructureArray(recipe, 'instructions');
        return recipe 
    }

    // convert the array into a dictionary with the index as the key 
    // this allow us to CRUD specific items in an array in our form 
    $scope.restructureArray = function(recipe, key) { 
        var original = recipe[key]; 
        recipe[key] = {};
        for (var i=0; i < original.length; i++) {
            recipe[key][i] = original[i]; 
        }
        return recipe[key]; 
    }

    // hide a "delete" item from the view 
    $scope.removeFromView = function() {
        // in progress 
    }

    $scope.saveRecipe = function() {
    	return $http.post('/api/recipe/' + urlKey + '/save', $scope.recipe).then(
    		function successCallback() {
                $scope.message = 'success'; 
                console.log("success"); 
    		}, function errorCallback() {
    			$scope.message = "error";
                console.log("error");  
    		}
    	)
    }
}]);

