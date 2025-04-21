from app.schemas.credit import CreditPackage

class CreditService:
    PACKAGES = {
        CreditPackage.REGULAR: {"credits": 100, "usd": 10},
        CreditPackage.PLUS: {"credits": 300, "usd": 40},
        CreditPackage.PRO: {"credits": 500, "usd": 60}
    }

    @classmethod
    def get_package_details(cls, package: CreditPackage):
        return cls.PACKAGES[package]