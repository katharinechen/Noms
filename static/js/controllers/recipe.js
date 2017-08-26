'use strict';

// controls the display of a single recipe
app.controller('Recipe', ['$scope', '$http', '$window', '$mdDialog', function($scope, $http, $window, $mdDialog) {
    $scope.arraySections = ['tags', 'ingredients', 'instructions'];  

    var urlKey = $scope.preload.urlKey;
    $http({method: 'GET', url: '/api/recipe/' + urlKey}).then(function(recipe) {
        $scope.recipe = $scope.buildRecipeObjects(recipe.data); 
    });

    // create a recipe object that is easy for the front-end to use
    // to use angular-xeditable, array with strings must be transformed into array with objects 
    $scope.buildRecipeObjects = function(data) { 
        for (var a=0; a < $scope.arraySections.length; a++) { 
            var section = data[$scope.arraySections[a]]; 
            var newArray = []; 
            for (var i=0; i < section.length; i++) { 
                var newObj = {"description": section[i]}; 
                newArray.push(newObj); 
            }
            data[$scope.arraySections[a]] = newArray; 
        }; 
        return data; 
    };

    // teardown recipe object transformations 
    // array with objects are transformed back into array with strings 
    $scope.tearDownRecipeObjects = function(data) { 
        for (var a=0; a < $scope.arraySections.length; a++) { 
            var section = data[$scope.arraySections[a]]; 
            var newArray = []; 
            for (var i=0; i < section.length; i++) { 
                newArray.push(section[i]['description']); 
            }
            data[$scope.arraySections[a]] = newArray; 
        }; 
        return data; 
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

    // delete recipe and redirect to recipe list page 
    $scope.deleteRecipe = function(recipe) { 
        return $http.post('/api/recipe/' + urlKey + '/delete').then(
            function successCallback() {
                console.log("yeah"); 
                $window.location.href = '/recipes'; 

            }, function errorCallback() {
                console.log("error"); 
            }
        )
    };

    // save editted recipe 
    $scope.saveRecipe = function() {
        var testy = JSON.parse(JSON.stringify($scope.recipe)); 
        $scope.sendBack = $scope.tearDownRecipeObjects(testy);
    	return $http.post('/api/recipe/' + urlKey + '/save', $scope.sendBack).then(
    		function successCallback() {
    		}, function errorCallback() {
    			$scope.message = "error";
    		}
    	)
    }; 

    $scope.showConfirm = function(ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.confirm()
              .title('Would you like to delete your debt?')
              .textContent('All of the banks have agreed to forgive you your debts.')
              .ariaLabel('Lucky day')
              .targetEvent(ev)
              .ok('Please do it!')
              .cancel('Sounds like a scam');

        $mdDialog.show(confirm).then(function() {
          $scope.status = 'You decided to get rid of your debt.';
        }, function() {
          $scope.status = 'You decided to keep your debt.';
        });
    };
}]);

