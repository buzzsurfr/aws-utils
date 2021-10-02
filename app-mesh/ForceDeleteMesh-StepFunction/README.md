# Force Delete Mesh

Delete a mesh and all dependent resources.

**NOTE:** This costs more to run than it's worth. Better to use [delete_mesh.py](https://github.com/buzzsurfr/aws-utils/blob/master/app-mesh/delete_mesh.py) instead.

## Input

```json
{
    "MeshName": "MyMeshName"
}
```

## State Machine

![ForceDeleteMesh](ForceDeleteMesh.svg)
