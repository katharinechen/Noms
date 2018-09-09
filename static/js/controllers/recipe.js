'use strict';

// Controller for a single recipe
app.controller('RecipeShow', ['$scope', '$window', '$mdDialog', 'recipeFactory', function($scope, $window, $mdDialog, recipeFactory) {

    // Initalize Variables
    $scope.status;
    $scope.message = '';
    $scope.recipe;
    $scope.arraySections = ['tags', 'ingredients', 'instructions'];
    var urlKey = $scope.preload.urlKey;

    // Read
    $scope.readRecipe = function(urlKey) {
        recipeFactory.read(urlKey)
            .then(function(response) {
                $scope.recipe = response.data;
            }), function (error) {
                $scope.status = "Unable to read the recipe data: " + error.message;
            }
    };
    $scope.readRecipe(urlKey);

    // Delete
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

        //Delete a single recipe
        $scope.deleteRecipe = function() {
            recipeFactory.delete(urlKey)
                .then(function(response) {
                    $window.location.href = '/recipes';
                }), function (error) {
                    $scope.status = "Unable to delete customer data: " + error.message;
                }
        };
    };

    // Show recipe edit modal
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

    function DialogController($scope, $http, $mdDialog, recipe) {
        $scope.recipe = recipe;
        $scope.cancel = function() {
            $mdDialog.cancel();
        };

        // save edited recipe
        $scope.saveRecipe = function(recipe) {
            return $http.post('/api/recipe/' + urlKey + '/save', recipe).then(
                function successCallback() {
                    $scope.saveAlert();
                }, function errorCallback() {
                    $scope.errorAlert();
                }
            );
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
    }

    //     // testing stuff
    //     $scope.editComment = function(event, recipe, ingredientIndex) {

    //         console.log("I am here");
    //         console.log("recipe: " + recipe);
    //         console.log("ingredientIndex:" + ingredientIndex);

    //         var editDialog = {
    //           modelValue: recipe.ingredients[ingredientIndex],
    //           placeholder: 'Add a comment',
    //           save: function (input) {
    //             dessert.comment = input.$modelValue;
    //           },
    //           targetEvent: event,
    //           title: 'Add a comment',
    //         //   validators: {
    //         //     'md-maxlength': 30
    //         //   }
    //         };

    //         // how do I make mdEditDialog work????
    //         var promise;
    //         promise = $mdEditDialog.small(editDialog);
    //         promise.then(function (ctrl) {
    //           var input = ctrl.getInput();
    //          // not sure what this does
    //           input.$viewChangeListeners.push(function () {
    //             input.$setValidity('test', input.$modelValue !== 'test');
    //           });
    //         });
    //       };
    // }




}]);



