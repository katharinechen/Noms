"use strict";


describe("static/js/controllers/navbar.js : NavbarCtrl", () => {
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
        $controller("Preload", {$scope: $rootScope, $window: $window});
        $controller("NavbarCtrl", {$scope: $rootScope});
    }));

    beforeEach(() => {
        var user = {
            email: "unittest@example.com",
            givenName: "Unit",
            familyName: "Test",
            roles: ["user"]
        };
        this.$httpBackend.expectGET("/api/user").respond(user
        );
        this.$httpBackend.flush();
        expect(this.scope.user.email).to.equal("unittest@example.com");
    });

    it("should show an auth0 lock", () => {
        window.Auth0Lock = () => {};
        var lockThing = {"show": sinon.spy()};
        sinon.stub(window, "Auth0Lock").returns(lockThing);
        this.scope.showLogin();
        expect(lockThing.show.called).to.be.true;
    });

});
