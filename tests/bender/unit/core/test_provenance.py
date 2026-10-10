from bender.core.identity.models import Id, Namespace
from bender.core.provenance.models import ArtifactSource, OperationRecord, Provenance


def test_empty_provenance():
    prov = Provenance.empty()
    assert len(prov.sources) == 0
    assert prov.operation is None


def test_provenance_creation():
    id1 = Id.generate()
    ns1 = Namespace("test-domain")
    source = ArtifactSource(id=id1, namespace=ns1)

    op_id = Id.generate()
    op = OperationRecord(operation_id=op_id, version="1.0.0")

    prov = Provenance(sources=[source], operation=op)

    assert len(prov.sources) == 1
    assert prov.sources[0].id == id1
    assert prov.sources[0].namespace == ns1
    assert prov.operation.operation_id == op_id
    assert prov.operation.version == "1.0.0"
