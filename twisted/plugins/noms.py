from twisted.application.service import ServiceMaker

Noms = ServiceMaker(
    "Noms",
    "noms.cli",
    ("A noms application server"),
    "noms")
