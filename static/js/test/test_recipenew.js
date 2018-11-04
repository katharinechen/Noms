"use strict";


describe("static/js/controllers/recipe-create.js : CreateRecipeCtrl", () => {
    beforeEach(module("noms"));

    beforeEach(inject(($injector, $controller, $rootScope, $window, recipeFactory) => {
        this.$httpBackend = $injector.get("$httpBackend");
        this.scope = $rootScope;
        $window.nomsPreload = JSON.stringify(
            {
                auth0Public: "a;klsdjfha;lskdfj",
                apparentURL: "https://unittests.noms.com",
            }
        );
        $window.onbeforeunload = () => 'Oh no!';
        $controller("CreateRecipeCtrl", {$scope: $rootScope, recipeFactory});
    }));

    it("should make a new recipe on save-click - success", () => {
        var ingredients, instructions, tags, response;
        ingredients = "butter\nmore butter";
        instructions = "put butter in a pan, put more butter in the same pan, enjoy";
        tags = "blah, blah1, blah2";
        var saveAlert = sinon.spy(this.scope, "saveAlert");

        this.scope.saveNewRecipe({
            ingredients: ingredients,
            instructions: instructions,
            tags: tags,
        });
        response = {message: "mehhy", status: "yup"};
        this.$httpBackend.expectPOST("/api/recipe/create").respond(response);
        this.$httpBackend.flush();
        sinon.assert.calledOnce(saveAlert);
    });

    it("should make a new recipe on save-click - failure 403", () => {
        var response = {
            status: "error",
            message: "ono"
        };
        var errorAlert = sinon.spy(this.scope, "errorAlert");
        this.scope.saveNewRecipe({ingredients: "", instructions: "", tags: ""});
        this.$httpBackend.expectPOST("/api/recipe/create").respond(403, response);
        this.$httpBackend.flush();
        sinon.assert.calledOnce(errorAlert);
    });

    it("should make a new recipe on save-click - failure non-403", () => {
        var response = {
            status: "error",
            message: "ono"
        };
        var errorAlert = sinon.spy(this.scope, "errorAlert");
        this.scope.saveNewRecipe({ingredients: "", instructions: "", tags: ""});
        this.$httpBackend.expectPOST("/api/recipe/create").respond(404, response);
        this.$httpBackend.flush();
        sinon.assert.calledOnce(errorAlert);
    });
});
