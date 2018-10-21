"use strict";


describe("static/js/controllers/recipe-new.js : NewRecipeCtrl", () => {
    beforeEach(module("noms"));

    beforeEach(inject(($injector, $controller, $rootScope, $window) => {
        this.$httpBackend = $injector.get("$httpBackend");
        this.scope = $rootScope;
        $window.nomsPreload = JSON.stringify(
            {
                auth0Public: "a;klsdjfha;lskdfj",
                apparentURL: "https://unittests.noms.com",
            }
        );
        $controller("NewRecipeCtrl", {$scope: $rootScope});
    }));

    it("should make a new recipe on save-click if no error", () => {
        var ingredients, instructions, response;
        ingredients = ["butter", "more butter"];
        instructions = ["put butter in a pan", "put more butter in the same pan", "enjoy"];
        this.scope.update({ingredients: ingredients,
            instructions: instructions,
        });
        response = {message: "whatevers", status: "yup"};
        this.$httpBackend.expectPOST("/api/recipe/create").respond(response);
        this.$httpBackend.flush();
        expect(this.scope.message).to.equal("Done");
    });

    it("should show an error if save fails", () => {
        var response = {
            status: "error",
            message: "ono"
        };
        this.scope.update({ingredients: [], instructions: []});
        this.$httpBackend.expectPOST("/api/recipe/create").respond(response);
        this.$httpBackend.flush();
        expect(this.scope.message).to.equal("Error: ono");
    });

    it("should show a different error if there's a server error", () => {
        var response = {
            status: "error",
            message: "ono"
        };
        this.scope.update({ingredients: [], instructions: []});
        this.$httpBackend.expectPOST("/api/recipe/create").respond(403, response);
        this.$httpBackend.flush();
        expect(this.scope.message).to.equal("Server error with this request");
    });
});
