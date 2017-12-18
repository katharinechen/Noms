"use strict";


describe("static/js/controllers/navbar.js : NavbarCtrl", () => {
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
        $controller('NavbarCtrl', {$scope: $rootScope});
    }));

    it("should show an auth0 lock", () => {
        expect("me").to.equal("figure out how to do mocks");
    });

});
