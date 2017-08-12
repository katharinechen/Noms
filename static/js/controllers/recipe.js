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
        // reset the following attributes  
        recipe['ingredients'] = $scope.restructureArray(recipe, 'ingredients'); 
        recipe['instructions'] = $scope.restructureArray(recipe, 'instructions');
        return recipe 
    }

    // convert array of strings into array of dicts 
    $scope.restructureArray = function(recipe, category) { 
        var originalArray = recipe[category]; 
        var newArray = []; 
        for (var i=0; i < originalArray.length; i++) { 
            var newObj = {"index": i, "description": originalArray[i]}; 
            newArray.push(newObj); 
        }
        return newArray; 
    }; 

    // remove an item to an array 
    $scope.remove = function(catObj, index) {
        catObj.splice(index, 1); 
    }; 

    // add an item to an array 
    $scope.add = function(catObj) {
        var inserted = {
            "description": ''
        };
        catObj.push(inserted);
    };

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
    }; 
}]);

