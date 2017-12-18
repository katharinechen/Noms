"use strict";


describe("static/js/controllers/recipe.js : Recipe", () => {
    beforeEach(module("noms"));

    beforeEach(inject(($injector, $controller, $rootScope, $window) => {
        this.$httpBackend = $injector.get('$httpBackend');
        this.scope = $rootScope;
        $window.nomsPreload = '{"urlKey": "yummy-food"}';
        $controller('Preload', {$scope: $rootScope, $window: $window});
        $controller('Recipe', {$scope: $rootScope});
    }));

    it("should get a recipe", () => {
        var expected = {
                "name": 'recipeee',
                "author": 'mee',
                "user": 'me@me.com',
                "urlKey": 'yummy-food',
                "ingredients": [],
                "instructions": [],
                "recipeYield": '1 thing',
                "tags": [],
        };
        this.$httpBackend.expectGET('/api/recipe/yummy-food').respond(
        expected);
        this.$httpBackend.flush();
        expect(this.scope.recipe).to.deep.equal(expected);
    });
});
