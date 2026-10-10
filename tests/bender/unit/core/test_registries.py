def test_registry_imports():
    from bender.core.registries import (
        DomainRegistry,
        GraphicsExtensionRegistry,
        MethodRegistry,
        ProblemFamilyRegistry,
    )

    assert DomainRegistry is not None
    assert MethodRegistry is not None
    assert ProblemFamilyRegistry is not None
    assert GraphicsExtensionRegistry is not None
