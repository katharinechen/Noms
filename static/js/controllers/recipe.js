'use strict';

// controls the display of a single recipe
app.controller('Recipe', ['$scope', '$http', '$window', '$mdDialog', '$mdToast', '$location', function($scope, $http, $window, $mdDialog, $mdToast) {
    $scope.message = '';
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

    // save edited recipe
    $scope.saveRecipe = function() {
        var modifiedRecipe = JSON.parse(JSON.stringify($scope.recipe));
        $scope.sendBack = $scope.tearDownRecipeObjects(modifiedRecipe);
        return $http.post('/api/recipe/' + urlKey + '/save', $scope.sendBack).then(
            function successCallback() {
                $scope.saveAlert();
            }, function errorCallback() {
                $scope.errorAlert();
            }
        )
    };

    // delete recipe and redirect to recipe list page
    $scope.deleteRecipe = function(recipe) {
        return $http.post('/api/recipe/' + urlKey + '/delete').then(
            function successCallback() {
                $window.location.href = '/recipes';
            }, function errorCallback() {
            }
        )
    };

    // show recipe edit modal
    $scope.showEditModal = function(ev, recipe) {
        $mdDialog.show({
          controller: DialogController,
          templateUrl: '/static/js/partials/edit.html',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose:true,
          locals: {recipe: recipe},
        })
        .then(function(answer) {
            $scope.status = 'You said the information was "' + answer + '".';
        }, function() {
            $scope.status = 'You cancelled the dialog.';
        });
    };

    function DialogController($scope, $mdDialog, recipe) {
        $scope.recipe = recipe;
        $scope.hide = function() {
          $mdDialog.hide();
        };
        $scope.cancel = function() {
          $mdDialog.cancel();
        };
        $scope.answer = function(answer) {
          $mdDialog.hide(answer);
        };
    };


    // confirmation modal for deleting a recipe
    $scope.deleteConfirm = function(ev, recipe) {
        var confirm = $mdDialog.confirm()
              .title('Would you like to delete this recipe?')
              .textContent('This is a permanent change. You will not be able to restore this recipe after delection.')
              .targetEvent(ev)
              .ok('Yes')
              .cancel('No');
        $mdDialog.show(confirm).then(function() {
            $scope.deleteRecipe(recipe);
        });
    };

    // confirmation modal for saving a recipe
    $scope.saveAlert = function(ev){
        $mdDialog.show(
            $mdDialog.alert()
            .parent(angular.element(document.querySelector('#popupContainer')))
            .clickOutsideToClose(true)
            .title('Saved')
            .textContent('Your recipe was successfully saved. You did it!')
            .ok('Got it!')
            .targetEvent(ev)
        );
    };

    // confirmation modal for saving a recipe
    $scope.errorAlert = function(ev){
        $mdDialog.show(
            $mdDialog.alert()
            .parent(angular.element(document.querySelector('#popupContainer')))
            .clickOutsideToClose(true)
            .title('Error')
            .textContent("There was an error with your save. Won't it have been awesome if we told you why?")
            .ok('You suck!')
            .targetEvent(ev)
        );
    };
}]);
