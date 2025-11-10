import json
import boto3
import os
from jsonschema import validate, ValidationError
from botocore.exceptions import ClientError

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_PEDIDOS', 'ChinaWok-Pedidos')
table = dynamodb.Table(table_name)

# Tabla de productos
productos_table_name = os.environ.get('TABLE_PRODUCTOS', 'ChinaWok-Productos')
productos_table = dynamodb.Table(productos_table_name)

# Tabla de combos
combos_table_name = os.environ.get('TABLE_COMBOS', 'ChinaWok-Combos')
combos_table = dynamodb.Table(combos_table_name)

# Schema de validación
PEDIDO_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Pedidos",
    "type": "object",
    "properties": {
        "local_id": {"type": "string"},
        "pedido_id": {"type": "string"},
        "usuario_correo": {"type": "string", "format": "email"},
        "productos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string"},
                    "cantidad": {"type": "integer", "minimum": 1}
                },
                "required": ["nombre", "cantidad"],
                "additionalProperties": False
            },
            "minItems": 1
        },
        "combos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "combo_id": {"type": "string"},
                    "cantidad": {"type": "integer", "minimum": 1}
                },
                "required": ["combo_id", "cantidad"],
                "additionalProperties": False
            },
            "minItems": 1
        },
        "costo": {"type": "number", "minimum": 0},
        "direccion": {"type": "string"},
        "fecha_entrega_aproximada": {
            "type": ["string", "null"],
            "format": "date-time"
        },
        "estado": {
            "type": "string",
            "enum": ["procesando", "cocinando", "empacando", "enviando", "recibido"]
        },
        "historial_estados": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "estado": {
                        "type": "string",
                        "enum": ["procesando", "cocinando", "empacando", "enviando", "recibido"]
                    },
                    "hora_inicio": {"type": "string", "format": "date-time"},
                    "hora_fin": {"type": "string", "format": "date-time"},
                    "activo": {"type": "boolean"},
                    "empleado": {
                        "type": ["object", "null"],
                        "properties": {
                            "dni": {"type": "string"},
                            "nombre_completo": {"type": "string"},
                            "rol": {
                                "type": "string",
                                "enum": ["cocinero", "despachador", "repartidor"]
                            },
                            "calificacion_prom": {"type": "number", "minimum": 0, "maximum": 5}
                        },
                        "required": ["dni", "nombre_completo", "rol"]
                    }
                },
                "required": ["estado", "hora_inicio", "hora_fin", "activo"]
            },
            "minItems": 1
        }
    },
    "required": [
        "local_id",
        "pedido_id",
        "usuario_correo",
        "direccion",
        "costo",
        "estado",
        "historial_estados"
    ],
    "anyOf": [
        {"required": ["productos"]},
        {"required": ["combos"]}
    ],
    "additionalProperties": False
}


def verificar_productos_stock(local_id, productos):
    """
    Verifica que los productos existan y tengan stock suficiente
    Returns: (bool, str) - (éxito, mensaje de error)
    """
    for producto in productos:
        nombre = producto['nombre']
        cantidad = producto['cantidad']
        
        try:
            # Obtener producto de DynamoDB
            response = productos_table.get_item(
                Key={
                    'local_id': local_id,
                    'nombre': nombre
                }
            )
            
            if 'Item' not in response:
                return False, f"El producto '{nombre}' no existe en el local {local_id}"
            
            producto_db = response['Item']
            stock_disponible = producto_db.get('stock', 0)
            
            if stock_disponible < cantidad:
                return False, f"Stock insuficiente para '{nombre}'. Disponible: {stock_disponible}, Solicitado: {cantidad}"
                
        except ClientError as e:
            return False, f"Error al verificar producto '{nombre}': {str(e)}"
    
    return True, None


def verificar_combos(local_id, combos):
    """
    Verifica que los combos existan
    Returns: (bool, str) - (éxito, mensaje de error)
    """
    for combo in combos:
        combo_id = combo['combo_id']
        
        try:
            # Obtener combo de DynamoDB
            response = combos_table.get_item(
                Key={
                    'local_id': local_id,
                    'combo_id': combo_id
                }
            )
            
            if 'Item' not in response:
                return False, f"El combo '{combo_id}' no existe en el local {local_id}"
                
        except ClientError as e:
            return False, f"Error al verificar combo '{combo_id}': {str(e)}"
    
    return True, None


def handler(event, context):
    """
    Lambda handler para crear un pedido en DynamoDB
    """
    try:
        # Parsear el body del evento
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        # Validar schema
        validate(instance=body, schema=PEDIDO_SCHEMA)
        
        # Validar que tenga productos o combos
        if 'productos' not in body and 'combos' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Debe especificar al menos productos o combos'
                })
            }
        
        local_id = body.get('local_id')
        
        # Verificar productos si existen
        if 'productos' in body and body['productos']:
            exito, error_msg = verificar_productos_stock(local_id, body['productos'])
            if not exito:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Error de validación de productos',
                        'message': error_msg
                    })
                }
        
        # Verificar combos si existen
        if 'combos' in body and body['combos']:
            exito, error_msg = verificar_combos(local_id, body['combos'])
            if not exito:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Error de validación de combos',
                        'message': error_msg
                    })
                }
        
        # Insertar en DynamoDB
        table.put_item(Item=body)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Pedido creado exitosamente',
                'data': body
            })
        }
        
    except ValidationError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error de validación',
                'message': str(e.message)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'message': str(e)
            })
        }
