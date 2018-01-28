"use strict";


describe("static/js/controllers/recipenew.js : NewRecipeCtrl", () => {
    beforeEach(module("noms"));

    beforeEach(inject(($injector, $controller, $rootScope, $window) => {
        this.$httpBackend = $injector.get('$httpBackend');
        this.scope = $rootScope;
        $window.nomsPreload = JSON.stringify(
            {
                auth0Public: "a;klsdjfha;lskdfj",
                apparentURL: "https://unittests.noms.com",
            }
        );
        $controller('NewRecipeCtrl', {$scope: $rootScope});
    }));

    it("should make a new recipe on save-click if no error", () => {
        var ingredients, instructions, response;
        ingredients = ['butter', 'more butter'];
        instructions = ['put butter in a pan', 'put more butter in the same pan', 'enjoy'];
        this.scope.update({ingredients: ingredients,
            instructions: instructions,
        });
        response = {message: 'whatevers', status: 'yup'};
        this.$httpBackend.expectPOST('/api/recipe/create').respond(response);
        this.$httpBackend.flush();
    });

    it("should show an error if save fails", () => {
        expect(false).to.be.true;
    });

});
