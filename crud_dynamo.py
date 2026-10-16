import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('prestamos_laboratorio')

# 1. CREATE (Registrar préstamo de equipo)
table.put_item(
    Item={
        'id_prestamo': 'PRES-2026-001',
        'matricula_alumno': '20230101',
        'nombre_alumno': 'Jesús Núñez',
        'equipo_prestado': 'Multímetro Digital Fluke 117',
        'estado_prestamo': 'PENDIENTE',
        'fecha_prestamo': '2026-10-15',
        'detalles_equipo': {'laboratorio': 'Electrónica', 'num_serie': 'FLK-9921'}
    }
)

# 2. READ (Consultar préstamo por Partition Key)
response = table.get_item(Key={'id_prestamo': 'PRES-2026-001'})

# 3. UPDATE (Registrar devolución del equipo)
table.update_item(
    Key={'id_prestamo': 'PRES-2026-001'},
    UpdateExpression="set estado_prestamo = :e, fecha_devolucion = :f",
    ExpressionAttributeValues={':e': 'DEVUELTO', ':f': '2026-10-15'}
)
# 4. DELETE (Eliminar préstamo)
table.delete_item(
    Key={'id_prestamo': 'PRES-2026-001'}
)
from boto3.dynamodb.conditions import Attr

# 5. SCAN - Consulta ineficiente
response = table.scan(
    FilterExpression=Attr('estado_prestamo').eq('PENDIENTE')
)