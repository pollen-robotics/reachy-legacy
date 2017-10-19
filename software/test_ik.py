import ikpy

chain = ikpy.chain.Chain.from_urdf_file(
    urdf_file='./hardware/URDF/robots/reachy.URDF',
    base_elements=['base'],
)
