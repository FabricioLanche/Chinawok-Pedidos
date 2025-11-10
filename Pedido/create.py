import json
import boto3
import os
from jsonschema import validate, ValidationError

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_PEDIDOS', 'ChinaWok-Pedidos')
table = dynamodb.Table(table_name)

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
